import re
import math

class CalcTool:


    # Разрешённые символы: цифры, операторы, скобки, буквы, пробелы, запятая, точка, процент, символ π
    SAFE_PATTERN = re.compile(r"^[0-9+\-*/()., eE^%πa-zA-Z_]*$")

    def __init__(self):
        # Берём всё из math (без приватных имён)
        self.allowed_names = {name: obj for name, obj in math.__dict__.items() if not name.startswith("__")}
        # Добавляем полезные алиасы
        self.allowed_names.update({
            "abs": abs,
            "round": round,
        })
        # Собственные функции
        def cube_root(x):
            # корректный вещественный кубический корень для отрицательных чисел
            try:
                x = float(x)
            except Exception:
                return float('nan')
            if x >= 0:
                return x ** (1.0/3.0)
            else:
                return -((-x) ** (1.0/3.0))

        self.allowed_names['cube_root'] = cube_root
        # дать доступ к символу pi также как pi
        self.allowed_names['pi'] = math.pi
        self.allowed_names['π'] = math.pi

    def _insert_implicit_multiplication(self, expr: str) -> str:
        # число( -> число*(
        expr = re.sub(r'(\d)\s*(\()', r'\1*\2', expr)
        # )число -> )*число
        expr = re.sub(r'(\))\s*(\d)', r'\1*\2', expr)
        # ) ( -> )*(
        expr = re.sub(r'(\))\s*(\()', r'\1*\2', expr)
        # числоπ или числоpi -> число*pi
        expr = re.sub(r'(\d)\s*(π|pi)', r'\1*\2', expr)
        # πчисло или pichislo -> pi*число
        expr = re.sub(r'(π|pi)\s*(\d|\()', r'\1*\2', expr)
        # идентификатор рядом с числом: sin2 -> sin*2
        expr = re.sub(r'([a-zA-Z_]+)\s*(\d)', r'\1*\2', expr)
        # число рядом с идентификатором: 2sin -> 2*sin
        expr = re.sub(r'(\d)\s*([a-zA-Z_]+)', r'\1*\2', expr)
        return expr

    def calculate(self, expression: str):
        """
        ssadfsdaasdfasf"""
        expr = expression.strip()

        # --- 🔹 Обработка надстрочных степеней ---
        superscript_map = {
            "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
            "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"
        }
        def replace_superscripts(expr):
            def repl(m):
                s = m.group(0)
                normal = ''.join(superscript_map[c] for c in s)
                return '**' + normal
            return re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+', repl, expr)
        expr = replace_superscripts(expr)
        # --- 🔹 конец вставки ---

        if not self.SAFE_PATTERN.match(expr):
            return "Ошибка: недопустимые символы в выражении."

        expr = expr.replace(',', '.')
        expr = expr.replace('π', 'pi')
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expr)
        expr = expr.replace('^', '**')
        expr = self._insert_implicit_multiplication(expr)

        try:
            result = eval(expr, {"__builtins__": {}}, self.allowed_names)
            if isinstance(result, float):
                result = round(result, 12)
            return result
        except Exception as e:
            return f"Ошибка вычисления: {e}"



# Тестовые примеры можно поместить ниже (в демонстрационных целях)
if __name__ == '__main__':
    calc = CalcTool()
    examples = [
        "4 * π * (cube_root(3*36π/(4π)))",
        "2pi + 3(4+5)",
        "sqrt(2)^2 + log(100,10)",
        "cube_root(-27) + abs(-5)",
        "120%",
        "factorial(6) + hypot(3,4)",
        "sin(pi/6) + cos(pi/3)",
        "round(2,3) + e",
        "(3+2)4 + 5pi",
        "(1/3) * (3 + 6)12² ",
        "3² + 4³"
    ]
    for ex in examples:
        print(ex, '->', calc.calculate(ex))
