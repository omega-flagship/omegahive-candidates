; Invented disposable projection. Rules are inspected local code, not catalogue
; contents to evaluate. Host visibility/custody and ranking are not implemented.
; This computes per-condition reports, not plans, assignments or a quality score.

(Need request-clean csv-to-table)
(Need request-conflict csv-to-table)
(Need request-unknown csv-to-table)
(Need request-changed csv-to-table)
(Requires request-clean offline)
(Requires request-conflict header-handling)
(Requires request-unknown capacity)
(Requires request-changed offline)
(Offer visible-code csv-to-table tree-v1)
(Offer changed-code csv-to-table tree-v2)
(Condition visible-code tree-v1 offline supported evidence-offline)
(Condition visible-code tree-v1 header-handling supported evidence-success)
(Condition visible-code tree-v1 header-handling contradicted evidence-adverse)
; Old verification belongs to the old tree, not changed-code's current offer.
(Condition changed-code tree-v1 offline supported old-tree-verification)
; Even though an internal fact is present, no visible Offer exists for hidden-code.
(Condition hidden-code tree-v1 offline supported hidden-evidence)

(= (assess-condition $need $offer $tree $condition)
   (let $facts
      (collapse (match &self (Condition $offer $tree $condition $status $ref)
         (ConditionAssessment $need $offer $tree $condition $status $ref)))
      (if (== $facts ())
          (ConditionAssessment $need $offer $tree $condition unknown no-record)
          (superpose $facts))))

(= (assess $need $offer)
   (match &self (Need $need $capability)
      (match &self (Offer $offer $capability $tree)
         (match &self (Requires $need $condition)
            (assess-condition $need $offer $tree $condition)))))

!(test (collapse (assess request-clean visible-code))
       ((ConditionAssessment request-clean visible-code tree-v1 offline supported evidence-offline)))
!(test (collapse (assess request-conflict visible-code))
       ((ConditionAssessment request-conflict visible-code tree-v1 header-handling supported evidence-success)
        (ConditionAssessment request-conflict visible-code tree-v1 header-handling contradicted evidence-adverse)))
!(test (collapse (assess request-unknown visible-code))
       ((ConditionAssessment request-unknown visible-code tree-v1 capacity unknown no-record)))
!(test (collapse (assess request-changed changed-code))
       ((ConditionAssessment request-changed changed-code tree-v2 offline unknown no-record)))
!(test (collapse (assess request-clean hidden-code)) ())
; Contradiction for one condition does not produce an arbitrary unrelated ability.
!(test (collapse (match &self (Offer visible-code database-migration $tree) $tree)) ())
