"""Public import of the self-contained program admission implementation."""
from .program.protocol import (ReuseAdmission, Refused, Admitted, BINDING_FIELDS,
                               ALERT_FIELDS, BASES, _binding)
from .program.protocol import admit_typed_need, admit_no_candidate
