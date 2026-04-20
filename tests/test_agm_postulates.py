# test_agm_postulates.py — Verification of AGM postulates
#
# Systematically tests that the revision operator satisfies all AGM postulates:
#
#   (*1) Closure      — B*φ is a belief set (closed under logical consequence)
#   (*2) Success      — φ ∈ B*φ
#   (*3) Inclusion    — B*φ ⊆ B+φ
#   (*4) Vacuity      — If ¬φ ∉ B, then B*φ = B+φ
#   (*5) Consistency  — B*φ is consistent (unless φ is a contradiction)
#   (*6) Extensionality — If φ ≡ ψ, then B*φ = B*ψ
#
# Uses multiple randomly generated and hand-crafted belief bases + formulas.
