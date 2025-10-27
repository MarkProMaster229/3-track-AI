import math
import re

class CalcTool:
    """
    Безопасный обработчик арифметических выражений.
    Поддерживает функции из math и простые операторы.
    Исправляет неявное умножение, например 6(5+9) -> 6*(5+9)
    """

    # Разрешённые символы (числа, операции, скобки, буквы)
    SAFE_PATTERN = re.compile(r"^[0-9+\-*/()., eE^% ]*[a-zA-Z_]*[0-9+\-*/()., eE^% a-zA-Z_]*$")

    def __init__(self):
        # Разрешаем функции из math (sin, cos, sqrt, pi, e, log и т.п.)
        self.allowed_names = {
            name: obj for name, obj in math.__dict__.items() if not name.startswith("__")
        }
        # Добавляем полезные алиасы
        self.allowed_names.update({
            "abs": abs,
            "round": round,
        })

    def fix_implicit_multiplication(self, expr: str) -> str:
        """
        Вставляет явное умножение там, где Python считает вызовом:
        6(5+9) -> 6*(5+9), (2+3)4 -> (2+3)*4
        """
        # Число перед скобкой
        expr = re.sub(r'(\d)\s*\(', r'\1*(', expr)
        # Скобка перед числом
        expr = re.sub(r'\)\s*(\d)', r')*\1', expr)
        # Число перед переменной/функцией (sin, cos и т.п.)
        expr = re.sub(r'(\d)\s*([a-zA-Z_])', r'\1*\2', expr)
        return expr

    def calculate(self, expression: str):
        """
        Вычисляет выражение безопасно. Возвращает число или строку с ошибкой.
        """
        expr = expression.strip()

        # Проверка на разрешённые символы
        if not self.SAFE_PATTERN.match(expr):
            return "Ошибка: недопустимые символы в выражении."

        # Исправляем неявное умножение
        expr = self.fix_implicit_multiplication(expr)

        # Приводим возведение в степень к Python-стилю (**)
        expr = expr.replace("^", "**")

        try:
            result = eval(expr, {"__builtins__": {}}, self.allowed_names)
            # Округляем красиво, если это float
            if isinstance(result, float):
                result = round(result, 10)
            return result
        except Exception as e:
            return f"Ошибка вычисления: {e}"

# ======== Пример использования ========
if __name__ == "__main__":
    calc = CalcTool()
    print(calc.calculate("2 + 3 * 4"))             # 14
    print(calc.calculate("(3 + 4)**2"))            # 49
    print(calc.calculate("sin(pi / 2)"))           # 1.0
    print(calc.calculate("sqrt(16) + log(10, 10)")) # 5.0
    print(calc.calculate("2 ** 100"))              # 1267650600228229401496703205376
    print(calc.calculate("6(5+9)"))                # 84
    print(calc.calculate("(2+3)4"))                # 20
    print(calc.calculate("5*6(5+9)"))              # 420
    print(calc.calculate("os.system('rm -rf /')")) # Ошибка: недопустимые символы
