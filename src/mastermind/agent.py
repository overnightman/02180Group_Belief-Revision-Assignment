# agent.py — Belief-revision–based Mastermind code-breaker
#
# Uses the belief revision engine to play Mastermind:
#   1. Initialize belief base with background knowledge (game rules encoded
#      as propositional formulas) and an initial guess.
#   2. After each guess, receive feedback (black/white pegs).
#   3. Encode the feedback as a propositional formula.
#   4. Revise the belief base with the feedback formula.
#   5. Derive the next guess from the revised belief base.
#   6. Repeat until the code is cracked.
