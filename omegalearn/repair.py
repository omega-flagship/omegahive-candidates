"""Narrow suffix-repair learner: input/output pairs induce a declarative rule.

Never executes learnt MeTTa. Receiver uses an explicit bounded interpreter.
"""
from .core import Refused

def missing_closer(text):
    if not isinstance(text,str) or len(text)>10000: return None
    depth=0; quoted=False; escaped=False
    for ch in text:
        if ch=='"' and not escaped: quoted=not quoted
        elif not quoted:
            if ch=='(': depth+=1
            elif ch==')':
                depth-=1
                if depth<0: return None
        escaped=(ch=='\\' and not escaped)
    if quoted or not text.lstrip().startswith('('): return None
    return depth

def learn(examples):
    if len(examples)<2: raise Refused('insufficient examples')
    suffixes=[]
    for before,after in examples:
        if missing_closer(before)!=1 or missing_closer(after)!=0 or not after.startswith(before):
            raise Refused('unsupported repair example')
        suffixes.append(after[len(before):])
    if len(set(suffixes))!=1 or suffixes[0]!=')': raise Refused('inconsistent repair')
    return {'rules':['(= (learned-repair MissingOneCloser) AppendOneCloser)'],
            'procedure':{'id':'repair-one-closer','steps':['check-one-unclosed-delimiter','append-one-closer','return-for-parser-validation'],
                         'prerequisites':['complete-expression','no-unclosed-quote','receiver-parser-validation']},
            'track_record_refs':[]}

def apply(content,text):
    if content.get('rules')!=['(= (learned-repair MissingOneCloser) AppendOneCloser)']:
        raise Refused('unsupported declarative skill')
    return text+')' if missing_closer(text)==1 else None
