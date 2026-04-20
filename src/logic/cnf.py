# cnf.py — Conjunctive Normal Form conversion
#
# Converts an arbitrary propositional formula (AST) into CNF.
# Steps:
#   1. Eliminate biconditionals  (φ ↔ ψ) ≡ (φ → ψ) ∧ (ψ → φ)
#   2. Eliminate implications     (φ → ψ) ≡ (¬φ ∨ ψ)
#   3. Push negations inward     (De Morgan's laws, double negation elimination)
#   4. Distribute ∨ over ∧       to reach a conjunction of disjunctions
#
# The output is a set of clauses, where each clause is a frozenset of literals.
