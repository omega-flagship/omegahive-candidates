; Invented, offline facts only. Scope filtering is supplied by a synthetic
; host projection, not proven here. No grounded operations or code execution.
(Need need-code csv-to-table Csv Table)
(Need need-planner planning Goal Plan)
(Need incompatible csv-to-table Csv Database)
(Offer offer-code code:synthetic csv-to-table Csv Table
       (Workspace synthetic/csv.py tree-v1 parse_rows))
(Offer offer-planner swarm:synthetic-planner planning Goal Plan
       (Service planning service-v1))

(= (reuse $need)
   (match &self (Need $need $cap $in $out)
      (match &self (Offer $offer $provider $cap $in $out $location)
         (ReuseCandidate $need $offer $provider $location))))

!(test (collapse (reuse need-code))
       ((ReuseCandidate need-code offer-code code:synthetic
          (Workspace synthetic/csv.py tree-v1 parse_rows))))
!(test (collapse (reuse need-planner))
       ((ReuseCandidate need-planner offer-planner swarm:synthetic-planner
          (Service planning service-v1))))
!(test (collapse (reuse incompatible)) ())
!(test (collapse (reuse absent)) ())
