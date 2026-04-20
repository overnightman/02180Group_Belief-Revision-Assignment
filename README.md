# Belief Revision Engine

**02180 Introduction to AI — Spring 2025, DTU**

A propositional-logic belief revision engine implementing AGM revision, partial meet contraction, and resolution-based entailment — all from scratch (no SAT-solver libraries).

---

## Project Structure

```
02180Group_Belief-Revision-Assignment/
│
├── main.py                      # Entry point — interactive demo / CLI
├── requirements.txt             # Python dependencies (only pytest)
├── ReadMe.md                    # This file
│
├── src/                         # Source code
│   ├── __init__.py
│   │
│   ├── logic/                   # Layer 1: Propositional logic primitives
│   │   ├── __init__.py
│   │   ├── syntax.py            #   Formula AST + string parser
│   │   ├── cnf.py               #   CNF conversion pipeline
│   │   └── resolution.py        #   Resolution-based entailment checking
│   │
│   ├── belief_base/             # Layer 2: Belief revision operations
│   │   ├── __init__.py
│   │   ├── belief_base.py       #   Core data structure + expansion
│   │   ├── contraction.py       #   Partial meet contraction
│   │   └── revision.py          #   AGM revision (Levi identity)
│   │
│   └── mastermind/              # Layer 3 (optional): Mastermind game
│       ├── __init__.py
│       ├── game.py              #   Game engine (secret code, feedback)
│       └── agent.py             #   AI code-breaker using belief revision
│
└── tests/                       # Tests
    ├── __init__.py
    ├── test_syntax.py           #   Formula parsing & AST
    ├── test_cnf.py              #   CNF conversion
    ├── test_resolution.py       #   Entailment checking
    ├── test_belief_base.py      #   Belief base ops (add, remove, expand)
    ├── test_contraction.py      #   Partial meet contraction
    ├── test_revision.py         #   AGM revision
    └── test_agm_postulates.py   #   ★ AGM postulate verification
```

---

## Architecture

Three layers, each depending only on the one below it:

```
┌─────────────────────────────────────────┐
│  Layer 3 (optional): Mastermind Agent   │  game logic + belief-revision AI
├─────────────────────────────────────────┤
│  Layer 2: Belief Revision               │  belief base, contraction, revision
├─────────────────────────────────────────┤
│  Layer 1: Propositional Logic           │  formulas, CNF, resolution
└─────────────────────────────────────────┘
```

### Layer 1 — `src/logic/`

| File | Responsibility |
|------|----------------|
| **`syntax.py`** | Formula AST nodes (`Atom`, `Not`, `And`, `Or`, `Implies`, `Biconditional`) and a parser that converts strings like `"p & (q \| ~r) -> s"` into AST objects. |
| **`cnf.py`** | Converts any formula into CNF (a set of clauses). Pipeline: eliminate biconditionals → eliminate implications → push negations inward (De Morgan) → distribute ∨ over ∧. |
| **`resolution.py`** | Resolution refutation to check `KB ⊨ φ`: negate φ, convert `KB ∧ ¬φ` to CNF, resolve clause pairs until the empty clause is found (entailment holds) or no new clauses can be derived (entailment fails). |

### Layer 2 — `src/belief_base/`

| File | Responsibility |
|------|----------------|
| **`belief_base.py`** | Core data structure: a set of `(formula, priority)` pairs. The priority doubles as the **epistemic entrenchment** degree — higher priority = harder to retract. Provides `add` (expansion), `remove`, `entails`, and `is_consistent` methods. |
| **`contraction.py`** | Partial meet contraction `B ÷ φ`: computes remainder sets (maximal subsets of B not entailing φ), applies a **selection function** guided by formula priorities, and returns their intersection. |
| **`revision.py`** | AGM revision via the **Levi identity**: `B * φ = (B ÷ ¬φ) + φ`. Contracts by ¬φ first (remove contradictions), then expands with φ. |

### Layer 3 — `src/mastermind/` (optional)

| File | Responsibility |
|------|----------------|
| **`game.py`** | Mastermind game engine: secret code generation, feedback computation (black/white pegs), game loop. |
| **`agent.py`** | AI code-breaker: encodes game rules as propositional formulas, maintains a belief base, and revises it with feedback after each guess to derive the next guess. |

### Why no `ordering.py` or `expansion.py`?

- **Ordering** — Epistemic entrenchment is simply the `priority` field stored on each belief in `belief_base.py`. The selection function that uses it lives in `contraction.py`. A separate file would just add indirection.
- **Expansion** — Expansion is `B + φ = B ∪ {φ}`, which is a single method (`add`) on `BeliefBase`. It doesn't warrant its own module.

---

## Data Flow

```
User input: formula φ (string)
        │
        ▼
   ┌──────────┐
   │  Parser   │  syntax.py: string → AST
   └─────┬─────┘
         │
         ▼
   ┌──────────┐
   │ Revision  │  revision.py: B * φ = (B ÷ ¬φ) + φ
   └─────┬─────┘
         │
    ┌────┴──────────────────────┐
    │                           │
    ▼                           ▼
┌────────────┐          ┌────────────┐
│ Contraction │          │ Expansion  │
│   B ÷ ¬φ   │          │  B' + φ    │
└─────┬──────┘          └────────────┘
      │
      ├─ Compute remainder sets
      │    └─ resolution.py (entailment checks)
      │         └─ cnf.py (CNF conversion)
      │
      └─ Select best remainders (by priority)

Output: revised belief base B*φ
```

---

## How to Run

```bash
# Setup
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Run the engine
python main.py

# Run all tests
pytest

# Run AGM postulate verification
pytest tests/test_agm_postulates.py -v
```

---

## Assignment Checklist

- [ ] **Stage 1** — Belief base design & implementation (`belief_base.py`)
- [ ] **Stage 2** — Resolution-based entailment (`syntax.py`, `cnf.py`, `resolution.py`)
- [ ] **Stage 3** — Contraction (`contraction.py`)
- [ ] **Stage 4** — Expansion & revision (`belief_base.py:add`, `revision.py`)
- [ ] **Testing** — AGM postulate verification (`test_agm_postulates.py`)
- [ ] **Optional** — Mastermind (`game.py`, `agent.py`)
- [ ] **Report** — 4–6 page PDF
- [ ] **Declaration** — Division of labour PDF
