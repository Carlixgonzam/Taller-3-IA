"""
cnf.py — Transformations to Conjunctive Normal Form (CNF).
The full to_cnf() pipeline calls every transformation in order.
"""

from __future__ import annotations

from src.logic.propositional.ast import And, Atom, Formula, Iff, Implies, Not, Or


# --- GUIDED FUNCTION PROVIDED IN FULL ---


def eliminate_double_negation(formula: Formula) -> Formula:
    """
    Eliminate double negations recursively.

    Transformation:
        Not(Not(a)) -> a

    Applied recursively until no double negations remain.

    Example:
        >>> eliminate_double_negation(Not(Not(Atom('p'))))
        Atom('p')
        >>> eliminate_double_negation(Not(Not(Not(Atom('p')))))
        Not(Atom('p'))
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        if isinstance(formula.operand, Not):
            return eliminate_double_negation(formula.operand.operand)
        return Not(eliminate_double_negation(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_double_negation(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_double_negation(d) for d in formula.disjuncts))
    return formula


# --- FUNCTIONS STUDENTS MUST IMPLEMENT ---


def eliminate_iff(formula: Formula) -> Formula:
    """
    Eliminate biconditionals recursively.

    Transformation:
        Iff(a, b) -> And(Implies(a, b), Implies(b, a))

    Must be applied recursively to all sub-formulas.

    Example:
        >>> eliminate_iff(Iff(Atom('p'), Atom('q')))
        And(Implies(Atom('p'), Atom('q')), Implies(Atom('q'), Atom('p')))

    Hint: Use pattern matching on the formula type.
          For each type, apply eliminate_iff recursively to the operands,
          and only transform when you find an Iff.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement eliminate_iff()")


def eliminate_implication(formula: Formula) -> Formula:
    """
    Eliminate implications recursively.

    Transformation:
        Implies(a, b) -> Or(Not(a), b)

    Must be applied recursively to all sub-formulas.

    Example:
        >>> eliminate_implication(Implies(Atom('p'), Atom('q')))
        Or(Not(Atom('p')), Atom('q'))

    Hint: Similar to eliminate_iff. Recurse and transform
          only Implies nodes.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement eliminate_implication()")

def push_negation_inward(formula: Formula) -> Formula:
    """
    Apply De Morgan's laws and push negations toward atoms.

    Transformations:
        Not(And(a, b, ...)) -> Or(Not(a), Not(b), ...)   (De Morgan)
        Not(Or(a, b, ...))  -> And(Not(a), Not(b), ...)   (De Morgan)

    Must be applied recursively to all sub-formulas.

    Example:
        >>> push_negation_inward(Not(And(Atom('p'), Atom('q'))))
        Or(Not(Atom('p')), Not(Atom('q')))
        >>> push_negation_inward(Not(Or(Atom('p'), Atom('q'))))
        And(Not(Atom('p')), Not(Atom('q')))

    Hint: When you find a Not, inspect what is inside:
          - If Not(And(...)): apply De Morgan to turn into Or of negations.
          - If Not(Or(...)): apply De Morgan to turn into And of negations.
          - If Not(Atom): leave as is.
          For And and Or without a Not above, just recurse on the children.

    Note: This function is called AFTER eliminating Iff and Implies,
          so you need not handle those types.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement push_negation_inward()")

def distribute_or_over_and(formula: Formula) -> Formula:
    """
    Distribute Or over And to obtain CNF.

    Transformation:
        Or(A, And(B, C)) -> And(Or(A, B), Or(A, C))

    Must be applied recursively until no Or contains an And.

    Example:
        >>> distribute_or_over_and(Or(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Atom('p'), Atom('q')), Or(Atom('p'), Atom('r')))

    Hint: For an Or node, first distribute recursively on the children.
          Then check whether any child is an And. If so, apply the
          distribution and recurse on the result (there may be more).
          For And, simply recurse on each conjunct.
          Atoms and Not are returned unchanged.

    Note: This function is called AFTER pushing negations inward,
          so you will only see Atom, Not(Atom), And, and Or.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement distribute_or_over_and()")

def flatten(formula: Formula) -> Formula:
    """
    Flatten nested conjunctions and disjunctions.

    Transformations:
        And(And(a, b), c) -> And(a, b, c)
        Or(Or(a, b), c)   -> Or(a, b, c)

    Must be applied recursively.

    Example:
        >>> flatten(And(And(Atom('a'), Atom('b')), Atom('c')))
        And(Atom('a'), Atom('b'), Atom('c'))
        >>> flatten(Or(Or(Atom('a'), Atom('b')), Atom('c')))
        Or(Atom('a'), Atom('b'), Atom('c'))

    Hint: For an And, walk each child. If a child is also And,
          extend with its conjuncts instead of nesting the And.
          Same for Or with its disjuncts.
          If only one element remains, return it directly.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement flatten()")

# --- FULL PIPELINE ---


def to_cnf(formula: Formula) -> Formula:
    """
    [GIVEN] Full CNF conversion pipeline.

    Applies every transformation in the correct order:
    1. Eliminate biconditionals (Iff)
    2. Eliminate implications (Implies)
    3. Push negations inward (Not)
    4. Eliminate double negations (Not Not)
    5. Distribute Or over And
    6. Flatten conjunctions/disjunctions

    Example:
        >>> to_cnf(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Not(Atom('p')), Atom('q')), Or(Not(Atom('p')), Atom('r')))
    """
    formula = eliminate_iff(formula)
    formula = eliminate_implication(formula)
    formula = push_negation_inward(formula)
    formula = eliminate_double_negation(formula)
    formula = distribute_or_over_and(formula)
    formula = flatten(formula)
    return formula
