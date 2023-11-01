import ast
from typing import Optional


class ConditionalError(Exception):
    """ Exception during evaluating Conditionals

    This exception is raised if anything
    goes wrong during the evaluation of
    Conditionals.

    """
    pass


class Conditional():
    """ Evaluates conditional statements
        Currently supported operations:
            * not var
            * var
            * None
            * var1 == var2
            * var1 != var2
            * var1 is var2
            * var1 is not var2
            * var1 < var2
            * var1 <= var2
            * var1 > var2
            * var1 >= var2
    """
    @classmethod
    def compare_value(cls, name: ast.Constant | ast.Name):
        if isinstance(name, ast.Name):
            return name.id
        elif isinstance(name, ast.Constant):
            return int(name.value)
        else:
            raise ConditionalError('part is neither a name nor constant')

    @classmethod
    def validate_not(cls, expression: ast.UnaryOp) -> bool:
        if isinstance(expression.operand, ast.Name | ast.Constant):
            right = cls.compare_value(expression.operand)
            return not right
        else:
            raise ConditionalError("Unknown expression operand in 'not'")

    @classmethod
    def compare(cls, expression: ast.Compare) -> bool:
        if not isinstance(expression.left, ast.Name | ast.Constant):
            raise ConditionalError("Unknown left-operand in 'compare'")
        left = cls.compare_value(expression.left)
        if not isinstance(expression.comparators[0], ast.Name | ast.Constant):
            raise ConditionalError("Unknown right-operand in 'compare'")
        right = cls.compare_value(expression.comparators[0])
        op = expression.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        elif isinstance(op, ast.NotEq):
            return left != right
        elif isinstance(op, ast.Gt):
            return left > right
        elif isinstance(op, ast.Lt):
            return left < right
        elif isinstance(op, ast.LtE):
            return left <= right
        elif isinstance(op, ast.GtE):
            return left >= right
        elif isinstance(op, ast.Is):
            return left is right
        elif isinstance(op, ast.IsNot):
            return left is not right
        else:
            raise ConditionalError('Unknown compare operation')

    @classmethod
    def test(cls, condition: Optional[str]) -> bool:
        if not condition:
            return False
        expr = ast.parse(condition, mode='eval')
        if isinstance(expr.body, ast.Name):
            return True
        elif isinstance(expr.body, ast.Compare):
            return cls.compare(expr.body)
        elif isinstance(expr.body, ast.Name):
            return True
        elif isinstance(expr.body, ast.Constant):
            if expr.body.value:
                return True
            else:
                return False
        elif isinstance(expr.body, ast.UnaryOp):
            if isinstance(expr.body.op, ast.Not):
                return cls.validate_not(expr.body)
            else:
                raise ConditionalError('Unknown unary operation')
        else:
            raise ConditionalError(f'Unknown Condition: {condition}')
