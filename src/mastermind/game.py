# game.py — Mastermind game engine
#
# Implements the traditional Mastermind game logic:
#   - Secret code generation (4 pegs, 6 colours)
#   - Feedback computation: (black pegs = correct colour + position,
#                            white pegs = correct colour, wrong position)
#   - Game loop: guess → feedback → repeat until solved or max guesses
#
# This module is game-logic only; the AI code-breaker lives in agent.py.
