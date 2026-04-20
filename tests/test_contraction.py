# test_contraction.py — Unit tests for partial meet contraction
#
# Tests:
#   - Contracting a belief that is entailed → belief removed
#   - Contracting a belief not in the base → base unchanged
#   - Priority ordering influences which formulas are kept
#   - Remainder set computation correctness
