# test_revision.py — Unit tests for AGM belief revision
#
# Tests:
#   - Revising with a consistent formula → formula in the base
#   - Revising with a contradictory formula → old contradicting beliefs removed
#   - Levi identity correctness: revision = contraction(¬φ) + expansion(φ)
