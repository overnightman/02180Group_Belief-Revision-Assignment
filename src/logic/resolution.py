# resolution.py — Resolution-based logical entailment
#
# Implements the resolution refutation procedure:
#   To check  KB ⊨ φ  (KB entails φ):
#     1. Convert KB ∧ ¬φ to CNF (set of clauses)
#     2. Repeatedly resolve pairs of clauses
#     3. If the empty clause □ is derived → KB ⊨ φ
#     4. If no new clauses can be derived → KB ⊭ φ
#
# This module is implemented from scratch (no SAT solver libraries),
# as required by the assignment.
