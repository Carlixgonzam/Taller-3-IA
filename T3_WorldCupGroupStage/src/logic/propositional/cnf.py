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
    # === INITIAL VERSION MI VERSION  ===
    # def eliminate_iff(formula):
    #     if isinstance(formula, Atom):
    #         return formula
    #     if isinstance(formula, Not):
    #         if isinstance(formula.operand, Not):
    #             return eliminate_iff(formula.operand.operand)
    #         return Not(eliminate_iff(formula.operand))
    #     if isinstance(formula, And):
    #         return And(*(eliminate_iff(a) for a in formula.conjuncts))
    #     if isinstance(formula, Or):
    #         return Or(*(eliminate_iff(b) for b in formula.conjuncts))
    #     if isinstance(formula, Implies):
    #     # no se
    #     if isinstance(formula, Iff):
    #         # return
    #
    # Prompts used to get to the final version:
    # 1. "intenté implementar mi primera version de eliminate_iff, pero no tengo muy claro como puedo hacer implies
    #       ni como funciona la recursión en el ulitmo caso de iff
    # === FINAL VERSION (active code) ===
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_iff(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_iff(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_iff(d) for d in formula.disjuncts))
    if isinstance(formula, Implies):
        return Implies(
            eliminate_iff(formula.antecedent), eliminate_iff(formula.consequent)
        )
    if isinstance(formula, Iff):
        left = eliminate_iff(formula.left)
        right = eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))
    return formula


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
    # Implementacion propia en 3 iteraciones; la IA no escribio codigo, solo
    # señala en que rama estaba el error y que pregunta hacerme para corregirlo
    #
    # v1 (mía, incompleta): en la rama Implies reconstruía otro Implies
    #     en lugar de transformarlo:
    #         return Implies(eliminate_implication(a), eliminate_implication(b))
    #     el bug no aplicaba la transformación, solo recursaba
    #
    # Prompt 1 a la IA: "listo ya hice mi versión eliminate_implication"
    # Respuesta: señaló que la rama Implies no transformaba nada, sin dar el código.
    #
    # v2 (mía, todavía mal): confundí la fórmula con la de eliminate_iff:
    #         return Or(Implies(a, b), Implies(b, a))
    #     Bug: es la descomposición de un bicondicional, no de una implicación.
    #
    # Prompt 2 a la IA: "listo, ya hice la corrección que me dijiste"
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_implication(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_implication(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_implication(d) for d in formula.disjuncts))
    if isinstance(formula, Implies):
        a = eliminate_implication(formula.antecedent)
        b = eliminate_implication(formula.consequent)
        return Or(Not(a), b)
    return formula
    # === END YOUR CODE ===


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
    # aca si full mi version
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, And):
        return And(*(push_negation_inward(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(push_negation_inward(d) for d in formula.disjuncts))
    if isinstance(formula, Not):
        operand = formula.operand
        if isinstance(operand, And):
            return Or(*(push_negation_inward(Not(c)) for c in operand.conjuncts))
        if isinstance(operand, Or):
            return And(*(push_negation_inward(Not(d)) for d in operand.disjuncts))
        return Not(push_negation_inward(operand))
    return formula

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
    # === HISTORIAL DE DESARROLLO (distribute_or_over_and) ===
    # Implementación propia; la IA no escribió código, solo corrió los tests,
    # identificó la línea exacta del error y explicó por qué violaba la
    # restricción de Or (mínimo 2 operandos), sin dar la corrección.
    #
    # v1 (mía, con bug): el "resto" de disyuntos siempre se envolvía en Or,
    # incluso cuando solo quedaba 1 elemento tras remover el And encontrado:
    #     resto = Or(*hijos)
    # Bug: Or exige len(disjuncts) >= 2 (ver ast.py); con 1 solo elemento
    # remanente (ej. Or(p, And(q, r))) esto lanzaba
    # ValueError: Or requires at least 2 operands.
    #
    # Prompt 1 a la IA: "revisa mi función distribute or over and a ver si está correcta"
    # Respuesta: corrió pytest -k DistributeOrOverAnd, mostró el traceback del
    #     ValueError en "resto = Or(*hijos)" y preguntó qué fórmula representa
    #     "el resto" cuando a la lista le queda un solo elemento, sin dar código.
    #
    # v2 / final (mía, corregida): distinguir el caso de 1 elemento restante.
    #
    # Prompt 2 a la IA: "listo mira la corrección que hice"
    # Respuesta: confirmó con pytest que el bug quedó resuelto (4/6 tests);
    #     los 2 restantes fallaban por NotImplementedError de flatten (no
    #     implementada aún), no por esta función, y lo verificó aparte
    #     comprobando equivalencia lógica completa en tabla de verdad.
    # === FINAL VERSION (active code) ===
    if isinstance(formula, Atom) or isinstance(formula, Not):
        return formula
    if isinstance(formula, And):
        return And(*(distribute_or_over_and(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        hijos = [distribute_or_over_and(d) for d in formula.disjuncts]
        for hijo in hijos:
            if isinstance(hijo, And):
                hijos.remove(hijo)
                if len(hijos) == 0:
                    return hijo
                if len(hijos) == 1:
                    resto = hijos[0]
                else:
                    resto = Or(*hijos)
                distribucion = []
                for c in hijo.conjuncts:
                    nuevo_or = Or(c, resto)
                    distribucion.append(distribute_or_over_and(nuevo_or))
                return And(*distribucion)
        return Or(*hijos)
    return formula
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
    # === HISTORIAL DE DESARROLLO (flatten) ===
    # Implementación propia; la IA no escribió código, solo corrió los tests,
    # identificó cuál caso fallaba y por qué, sin dar la corrección.
    #
    # v1 (mía, con bug): traté Not igual que Atom, devolviéndolo sin recursar
    # en su interior:
    #     if isinstance(formula, Atom) or isinstance(formula, Not):
    #         return formula
    # Bug: un Not puede envolver un And/Or anidado que también necesita
    # aplanarse (ej. Not(And(And(a,b), c))); al no recursar, el And interno
    # se quedaba sin aplanar.
    #
    # Prompt 1 a la IA: "listo ahora revisa mi funcion flatten"
    # Respuesta: corrió pytest -k Flatten, mostró que test_flatten_not fallaba
    #     (esperaba 3 conjuntos aplanados y solo había 2) y señaló que la rama
    #     Not necesitaba separarse de Atom y recursar con flatten(formula.operand),
    #     sin dar el código.
    #
    # v2 / final (mía, corregida): separé el caso Not del caso Atom.
    #
    # Prompt 2 a la IA: "ya hice la correción, ayudame a revisar que si está
    #     bien y pon los comentarios de las correciones que me hiciste"
    # Respuesta: confirmó con pytest (7/7 en Flatten, 42/42 en todo test_cnf.py
    #     incluyendo el pipeline to_cnf) que la corrección fue suficiente.
    # === FINAL VERSION (active code) ===
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(flatten(formula.operand))
    if isinstance(formula, And):
        hijos = [flatten(c) for c in formula.conjuncts]
        nuevos_hijos = []
        for hijo in hijos:
            if isinstance(hijo, And):
                nuevos_hijos.extend(hijo.conjuncts)
            else:
                nuevos_hijos.append(hijo)
        if len(nuevos_hijos) == 1:
            return nuevos_hijos[0]
        return And(*nuevos_hijos)
    if isinstance(formula, Or):
        hijos = [flatten(d) for d in formula.disjuncts]
        nuevos_hijos = []
        for hijo in hijos:
            if isinstance(hijo, Or):
                nuevos_hijos.extend(hijo.disjuncts)
            else:
                nuevos_hijos.append(hijo)
        if len(nuevos_hijos) == 1:
            return nuevos_hijos[0]
        return Or(*nuevos_hijos)
    return formula
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
