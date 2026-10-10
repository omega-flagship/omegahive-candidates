import pytest
from omegamatch.skill_metadata import project_skill_metadata

TEXT = '''; synthetic declarations
!(shell "never executed")
!(add-atom &skills (Skill "synthetic"))
!(add-atom &skills (SkillTopic "synthetic" "topic"))
!(add-atom &skills (SkillArg "synthetic" 1 "text" "input"))
!(add-atom &skills (Risk "synthetic" "external-effect"))
!(add-atom &skills (Effect "synthetic" "write"))
(SkillHelp "topic" "topic-level guidance")
(= (Skill "invented-dynamic") (shell "no"))
'''


def test_literal_wrapper_and_topic_help_are_metadata_not_authority():
    output = project_skill_metadata(TEXT, 'synthetic-file')
    assert len(output['offers']) == 1
    offer = output['offers'][0]
    assert offer['name'] == 'synthetic' and offer['arguments'] == [['1', 'text', 'input']]
    assert offer['risks'] == ['external-effect'] and offer['effects'] == ['write']
    assert offer['topic_help'] == [['topic', 'topic-level guidance']]
    assert 'runtime-loaded' in offer['unknowns'] and offer['tier'] == 'advertised'


def test_dynamic_and_other_space_facts_do_not_become_offers():
    text = '(= (Skill "dynamic") (x)) !(add-atom &private (Skill "private")) (Skill $variable)'
    assert project_skill_metadata(text, 'synthetic')['offers'] == []


def test_source_change_updates_digest_and_strings_remain_data():
    before = project_skill_metadata(TEXT, 'synthetic')
    after = project_skill_metadata(TEXT + '\n; changed', 'synthetic')
    assert before['source_digest'] != after['source_digest']
    assert project_skill_metadata('(Skill "x) !(shell nope)")', 'synthetic')['offers'][0]['name'] == 'x) !(shell nope)'


@pytest.mark.parametrize('text', ['(Skill "x"', ')' , '(' * 129])
def test_malformed_or_excessive_nesting_refused(text):
    with pytest.raises(ValueError): project_skill_metadata(text, 'synthetic')


def test_module_join_keeps_declarations_help_and_call_shapes_without_body():
    from omegamatch.skill_metadata import project_module_metadata
    sources = [{'ref': 'entry', 'text': '(Provides synthetic.module (Skill synthetic))'},
               {'ref': 'card', 'text': '(SkillTopic "synthetic" "topic") (Risk "synthetic" "write")'},
               {'ref': 'help', 'text': '(SkillHelp "topic" "topic-level help")'},
               {'ref': 'impl', 'text': '(= (synthetic $x) (shell $x)) (= (synthetic $x $y) (dangerous $y))'}]
    output = project_module_metadata('synthetic.module', sources)
    offer = output['offers'][0]
    assert offer['provides_declared'] is True
    assert offer['rule_head_shapes'] == [['$x', '$y'], ['$x']]
    assert offer['topic_help'] == [['topic', 'topic-level help']]
    assert 'dangerous' not in str(offer) and 'shell' not in str(offer)
    assert len(offer['source_refs']) == 4 and 'provider-binding' in offer['unknowns']
    assert project_module_metadata('synthetic.module', list(reversed(sources))) == output


def test_other_module_provides_does_not_create_offer():
    from omegamatch.skill_metadata import project_module_metadata
    assert project_module_metadata('mine', [{'ref': 'entry', 'text': '(Provides other (Skill hidden))'}])['offers'] == []


def test_source_boundaries_cannot_repair_malformed_files():
    from omegamatch.skill_metadata import project_module_metadata
    with pytest.raises(ValueError):
        project_module_metadata('mine', [{'ref': 'a', 'text': '('}, {'ref': 'b', 'text': ')'}])


def test_duplicate_source_identity_refused():
    from omegamatch.skill_metadata import project_module_metadata
    with pytest.raises(ValueError):
        project_module_metadata('mine', [{'ref': 'same', 'text': ''}, {'ref': 'same', 'text': ''}])


def test_loader_selection_retains_order_and_does_not_import():
    from omegamatch.skill_metadata import project_loader_selection
    text = '!(import! &self (library OmegaClaw-Core ./modules/b/entry.metta))\n!(import! &self (library OmegaClaw-Core ./modules/a/entry.metta))'
    output = project_loader_selection(text, 'synthetic-loader')
    assert [i['logical_path'] for i in output['imports']] == ['modules/b/entry.metta', 'modules/a/entry.metta']
    assert 'import-success' in output['unknowns'] and output['unsupported_imports'] == 0


def test_loader_dynamic_foreign_and_escape_paths_remain_gaps():
    from omegamatch.skill_metadata import project_loader_selection
    text = '!(import! &self $dynamic) !(import! &self (library other a)) !(import! &self (library OmegaClaw-Core ../escape))'
    output = project_loader_selection(text, 'synthetic-loader')
    assert output['imports'] == [] and output['unsupported_imports'] == 3


def test_nested_import_expression_is_not_a_literal_configuration():
    from omegamatch.skill_metadata import project_loader_selection
    output = project_loader_selection('(= (x) (import! &self (library OmegaClaw-Core a)))', 'synthetic')
    assert output['imports'] == []



def test_multiline_literal_help_preserved_as_data():
    from omegamatch.skill_metadata import project_module_metadata
    source = '(Skill "synthetic") (SkillTopic "synthetic" "topic") (SkillHelp "topic" "line one\nline two")'
    result = project_module_metadata('synthetic.module', [{'ref': 'synthetic', 'text': source}])
    assert result['offers'][0]['topic_help'] == [['topic', 'line one\nline two']]



def test_explicit_type_declarations_and_direct_help_remain_distinct_from_topic_help():
    from omegamatch.skill_metadata import project_module_metadata
    text = '(Provides mine (Skill synthetic)) (: synthetic (-> String Result)) (SkillHelp "synthetic" "direct help")'
    offer = project_module_metadata('mine', [{'ref': 'synthetic', 'text': text}])['offers'][0]
    assert offer['typed_signature_declarations'] == [['->', 'String', 'Result']]
    assert offer['skill_help'] == ['direct help'] and offer['topic_help'] == []
    assert 'signature-completeness' in offer['unknowns']


def test_conflicting_types_preserved_not_unified_or_promoted():
    from omegamatch.skill_metadata import project_module_metadata
    text = '(Skill "synthetic") (: synthetic (-> String Result)) (: synthetic (-> Number Other))'
    offer = project_module_metadata('mine', [{'ref': 'synthetic', 'text': text}])['offers'][0]
    assert len(offer['typed_signature_declarations']) == 2
    assert offer['signature_conflict_unresolved'] is True and offer['tier'] == 'advertised'


def test_nested_type_declaration_in_rule_body_not_extracted():
    from omegamatch.skill_metadata import project_module_metadata
    text = '(Skill "synthetic") (= (x) (: synthetic (-> Fake Result)))'
    offer = project_module_metadata('mine', [{'ref': 'synthetic', 'text': text}])['offers'][0]
    assert offer['typed_signature_declarations'] == []
