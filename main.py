# main.py — Entry point for the Belief Revision Engine
# Run this file to launch the interactive demo / CLI.

from src.logic.syntax import parse, Atom, Not
from src.belief_base.belief_base import BeliefBase
from src.belief_base.contraction import contract
from src.belief_base.revision import revise


def print_banner():
    print("=" * 60)
    print("  Belief Revision Engine — 02180 Introduction to AI")
    print("  DTU, Spring 2025")
    print("=" * 60)
    print()


def print_help():
    print("Commands:")
    print("  add <formula> [priority]   — Add a belief (expansion)")
    print("  revise <formula> [priority] — Revise the belief base")
    print("  contract <formula>         — Contract the belief base")
    print("  entails <formula>          — Check if the base entails a formula")
    print("  consistent                 — Check if the base is consistent")
    print("  show                       — Display all beliefs")
    print("  clear                      — Clear the belief base")
    print("  help                       — Show this help message")
    print("  quit                       — Exit")
    print()
    print("Formula syntax:")
    print("  atoms:   p, q, rain, my_var")
    print("  not:     ~p")
    print("  and:     p & q")
    print("  or:      p | q")
    print("  implies: p -> q")
    print("  bicond:  p <-> q")
    print("  parens:  (p | q) & r")
    print()


def show_beliefs(bb: BeliefBase):
    if len(bb) == 0:
        print("  (empty)")
    else:
        for i, (formula, priority) in enumerate(bb.get_beliefs(), 1):
            print(f"  {i}. {formula}  [priority={priority}]")
    print()


def main():
    print_banner()
    print_help()

    bb = BeliefBase()

    while True:
        try:
            raw = input("belief> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "quit" or cmd == "exit":
            print("Goodbye!")
            break

        elif cmd == "help":
            print_help()

        elif cmd == "show":
            print("Current belief base:")
            show_beliefs(bb)

        elif cmd == "clear":
            bb.clear()
            print("Belief base cleared.\n")

        elif cmd == "consistent":
            if bb.is_consistent():
                print("✓ The belief base is consistent.\n")
            else:
                print("✗ The belief base is INCONSISTENT.\n")

        elif cmd == "add":
            if len(parts) < 2:
                print("Usage: add <formula> [priority]\n")
                continue
            try:
                formula_str, priority = _parse_with_priority(parts[1])
                formula = parse(formula_str)
                bb.add(formula, priority)
                print(f"Added: {formula}  [priority={priority}]")
                show_beliefs(bb)
            except Exception as e:
                print(f"Error: {e}\n")

        elif cmd == "revise":
            if len(parts) < 2:
                print("Usage: revise <formula> [priority]\n")
                continue
            try:
                formula_str, priority = _parse_with_priority(parts[1])
                formula = parse(formula_str)
                bb = revise(bb, formula, priority)
                print(f"Revised with: {formula}  [priority={priority}]")
                show_beliefs(bb)
            except Exception as e:
                print(f"Error: {e}\n")

        elif cmd == "contract":
            if len(parts) < 2:
                print("Usage: contract <formula>\n")
                continue
            try:
                formula = parse(parts[1])
                bb = contract(bb, formula)
                print(f"Contracted by: {formula}")
                show_beliefs(bb)
            except Exception as e:
                print(f"Error: {e}\n")

        elif cmd == "entails":
            if len(parts) < 2:
                print("Usage: entails <formula>\n")
                continue
            try:
                formula = parse(parts[1])
                if bb.entails(formula):
                    print(f"✓ The belief base entails: {formula}\n")
                else:
                    print(f"✗ The belief base does NOT entail: {formula}\n")
            except Exception as e:
                print(f"Error: {e}\n")

        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands.\n")


def _parse_with_priority(text: str) -> tuple[str, float]:
    """Extract an optional trailing priority from a formula string.

    Examples:
        "p & q 2.5"  → ("p & q", 2.5)
        "p -> q"     → ("p -> q", 1.0)
    """
    tokens = text.rsplit(maxsplit=1)
    if len(tokens) == 2:
        try:
            priority = float(tokens[1])
            return tokens[0], priority
        except ValueError:
            pass
    return text, 1.0


if __name__ == "__main__":
    main()
