# src.logic — Propositional logic primitives
from src.logic.syntax import Formula, Atom, Not, And, Or, Implies, Biconditional, parse
from src.logic.cnf import to_cnf
from src.logic.resolution import entails, entails_from_formulas
