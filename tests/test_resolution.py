# test_resolution.py — Unit tests for resolution-based entailment
#
# Tests:
#   - Simple entailment: {p, p→q} ⊨ q
#   - Non-entailment: {p} ⊭ q
#   - Contradiction detection: {p, ¬p} ⊨ anything
#   - Tautology: ⊨ p ∨ ¬p
#   - Larger knowledge bases with multiple resolution steps
