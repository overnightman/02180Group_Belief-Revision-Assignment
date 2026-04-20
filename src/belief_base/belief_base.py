# belief_base.py — Core belief base data structure
#
# A belief base is a finite set of propositional formulas, each annotated
# with a priority / entrenchment degree (integer or float).
#
# Key responsibilities:
#   - Store (formula, priority) pairs
#   - Expose the logical closure via the entailment engine (resolution.py)
#   - Provide helpers: add, remove, contains, is_consistent, etc.
#   - Convert the entire base to a single CNF clause-set for resolution
