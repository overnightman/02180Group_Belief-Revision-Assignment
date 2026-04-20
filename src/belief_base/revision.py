# revision.py — AGM belief revision via the Levi identity
#
# Implements the AGM revision operator (*):
#
#   B * φ  =  (B ÷ ¬φ) + φ
#
# The Levi identity defines revision as:
#   1. First CONTRACT by ¬φ  (remove anything that would contradict φ)
#   2. Then EXPAND with φ     (add the new belief)
#
# This ensures the revised belief base is consistent (if φ is consistent)
# and contains φ (Success postulate).
#
# AGM revision postulates satisfied:
#   (*1) Closure, (*2) Success, (*3) Inclusion, (*4) Vacuity,
#   (*5) Consistency, (*6) Extensionality
