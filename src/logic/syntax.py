# syntax.py — Propositional logic formula representation
#
# Defines the AST (Abstract Syntax Tree) for propositional formulas:
#   - Atom(name)          : propositional variable, e.g. "p", "q"
#   - Not(formula)        : negation  ¬φ
#   - And(left, right)    : conjunction  φ ∧ ψ
#   - Or(left, right)     : disjunction  φ ∨ ψ
#   - Implies(left, right): implication  φ → ψ
#   - Biconditional(l, r) : biconditional  φ ↔ ψ
#
# Also provides a parser to convert string representations into AST nodes.
