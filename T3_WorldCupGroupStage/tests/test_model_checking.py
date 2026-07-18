"""
Automated tests for propositional model checking.

Run with: pytest tests/test_model_checking.py -v
"""

from src.logic.propositional.ast import And, Atom, Iff, Implies, Not, Or
from src.logic.propositional.model_checking import (
    check_entailment,
    check_satisfiable,
    check_valid,
    get_all_models,
    truth_table,
)


class TestGetAllModels:
    def test_single_atom(self):
        models = get_all_models({"p"})
        assert len(models) == 2
        values = {m["p"] for m in models}
        assert values == {True, False}

    def test_two_atoms(self):
        models = get_all_models({"p", "q"})
        assert len(models) == 4
        for m in models:
            assert set(m.keys()) == {"p", "q"}

    def test_three_atoms(self):
        models = get_all_models({"p", "q", "r"})
        assert len(models) == 8

    def test_empty_atoms(self):
        models = get_all_models(set())
        assert len(models) == 1
        assert models[0] == {}

    def test_all_combinations_present(self):
        models = get_all_models({"a", "b"})
        combos = {(m["a"], m["b"]) for m in models}
        assert combos == {
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        }


class TestCheckSatisfiable:
    def test_simple_satisfiable(self):
        sat, model = check_satisfiable(Atom("p"))
        assert sat is True
        assert model is not None
        assert model["p"] is True

    def test_contradiction_unsatisfiable(self):
        formula = And(Atom("p"), Not(Atom("p")))
        sat, model = check_satisfiable(formula)
        assert sat is False
        assert model is None

    def test_disjunction_satisfiable(self):
        formula = Or(Atom("p"), Atom("q"))
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model is not None

    def test_complex_satisfiable(self):
        formula = And(Implies(Atom("p"), Atom("q")), Atom("p"))
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model is not None
        assert model["p"] is True
        assert model["q"] is True


class TestCheckValid:
    def test_tautology(self):
        formula = Or(Atom("p"), Not(Atom("p")))
        assert check_valid(formula) is True

    def test_not_tautology(self):
        assert check_valid(Atom("p")) is False

    def test_implication_tautology(self):
        formula = Implies(Atom("p"), Atom("p"))
        assert check_valid(formula) is True

    def test_double_negation_tautology(self):
        formula = Iff(Atom("p"), Not(Not(Atom("p"))))
        assert check_valid(formula) is True

    def test_modus_ponens_tautology(self):
        formula = Implies(
            And(Implies(Atom("p"), Atom("q")), Atom("p")),
            Atom("q"),
        )
        assert check_valid(formula) is True


class TestCheckEntailment:
    def test_simple_entailment(self):
        kb = [Implies(Atom("p"), Atom("q")), Atom("p")]
        assert check_entailment(kb, Atom("q")) is True

    def test_no_entailment(self):
        kb = [Implies(Atom("p"), Atom("q"))]
        assert check_entailment(kb, Atom("q")) is False

    def test_contradiction_entails_everything(self):
        kb = [Atom("p"), Not(Atom("p"))]
        assert check_entailment(kb, Atom("q")) is True

    def test_chain_entailment(self):
        kb = [
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Atom("p"),
        ]
        assert check_entailment(kb, Atom("r")) is True

    def test_empty_kb(self):
        """An empty KB only entails tautologies."""
        assert check_entailment([], Or(Atom("p"), Not(Atom("p")))) is True
        assert check_entailment([], Atom("p")) is False


class TestTruthTable:
    def test_simple_atom(self):
        table = truth_table(Atom("p"))
        assert len(table) == 2

    def test_conjunction(self):
        table = truth_table(And(Atom("p"), Atom("q")))
        assert len(table) == 4
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 1
        model = true_rows[0][0]
        assert model["p"] is True and model["q"] is True

    def test_implication(self):
        table = truth_table(Implies(Atom("p"), Atom("q")))
        assert len(table) == 4
        false_rows = [(m, r) for m, r in table if not r]
        assert len(false_rows) == 1
        model = false_rows[0][0]
        assert model["p"] is True and model["q"] is False

    def test_three_atoms(self):
        table = truth_table(And(Atom("p"), Atom("q"), Atom("r")))
        assert len(table) == 8
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 1

    def test_biconditional(self):
        """Iff(p, q): true in exactly 2 of 4 rows."""
        table = truth_table(Iff(Atom("p"), Atom("q")))
        assert len(table) == 4
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 2


class TestComplexSatisfiable:
    """Satisfiability tests with more complex structures."""

    def test_four_atom_satisfiable(self):
        """Formula with 4 atoms: implication chain + base fact."""
        formula = And(
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Implies(Atom("r"), Atom("s")),
            Atom("p"),
        )
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model["p"] is True
        assert model["q"] is True
        assert model["r"] is True
        assert model["s"] is True

    def test_xor_satisfiable(self):
        """XOR(p, q) = (p ∨ q) ∧ ¬(p ∧ q) — exactly one true."""
        xor = And(
            Or(Atom("p"), Atom("q")),
            Not(And(Atom("p"), Atom("q"))),
        )
        sat, model = check_satisfiable(xor)
        assert sat is True
        assert model is not None
        # Exactly one must be true
        assert model["p"] != model["q"]

    def test_xor_has_two_models(self):
        """XOR has exactly 2 satisfying models out of 4 possible."""
        xor = And(
            Or(Atom("p"), Atom("q")),
            Not(And(Atom("p"), Atom("q"))),
        )
        table = truth_table(xor)
        true_rows = [m for m, r in table if r]
        assert len(true_rows) == 2


class TestComplexValid:
    """Validity (tautology) tests with more complex formulas."""

    def test_de_morgan_tautology(self):
        """De Morgan: ¬(p ∧ q) ↔ (¬p ∨ ¬q)."""
        formula = Iff(
            Not(And(Atom("p"), Atom("q"))),
            Or(Not(Atom("p")), Not(Atom("q"))),
        )
        assert check_valid(formula) is True

    def test_hypothetical_syllogism(self):
        """Hypothetical syllogism: (p→q) ∧ (q→r) → (p→r)."""
        formula = Implies(
            And(
                Implies(Atom("p"), Atom("q")),
                Implies(Atom("q"), Atom("r")),
            ),
            Implies(Atom("p"), Atom("r")),
        )
        assert check_valid(formula) is True

    def test_disjunctive_syllogism(self):
        """Disjunctive syllogism: (p ∨ q) ∧ ¬p → q."""
        formula = Implies(
            And(Or(Atom("p"), Atom("q")), Not(Atom("p"))),
            Atom("q"),
        )
        assert check_valid(formula) is True

    def test_not_tautology_four_atoms(self):
        """(p ∧ q) → (r ∧ s) is not a tautology."""
        formula = Implies(
            And(Atom("p"), Atom("q")),
            And(Atom("r"), Atom("s")),
        )
        assert check_valid(formula) is False


class TestComplexEntailment:
    """Logical entailment tests with reasoning chains."""

    def test_modus_tollens(self):
        """Modus tollens: p→q, ¬q ⊨ ¬p."""
        kb = [Implies(Atom("p"), Atom("q")), Not(Atom("q"))]
        assert check_entailment(kb, Not(Atom("p"))) is True

    def test_resolution_chain(self):
        """Resolution chain: p→q, q→r, r→s, p ⊨ s."""
        kb = [
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Implies(Atom("r"), Atom("s")),
            Atom("p"),
        ]
        assert check_entailment(kb, Atom("s")) is True
