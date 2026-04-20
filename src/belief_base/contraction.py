# contraction.py — Partial meet contraction
#
# Implements the AGM contraction operator (÷) using the partial meet approach:
#
#   B ÷ φ  =  ∩ γ(B ⊥ φ)
#
# Where:
#   B ⊥ φ  = the set of all maximal subsets of B that do not entail φ
#             (called "remainder sets")
#   γ      = a selection function that picks the "best" remainder sets
#             guided by the epistemic entrenchment ordering (ordering.py)
#
# AGM contraction postulates satisfied:
#   (÷1) Closure, (÷2) Inclusion, (÷3) Vacuity,
#   (÷4) Success, (÷5) Recovery, (÷6) Extensionality
