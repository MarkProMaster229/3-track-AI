# tool_catcher.py
import re
import json
import requests
from bs4 import BeautifulSoup

#from tools.calc  import CalcTool
import re
import math

import re
import requests


class ToolCatcherImprovedSearch:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.0.0 Safari/537.36"
            )
        }

    def _clean_intro(self, text: str) -> str:
        """
        Убирает все скобочные вставки, но сохраняет пробелы, чтобы слова не слипались.
        Также удаляет [1], [2] и другие ссылки в квадратных скобках.
        """
        if not text:
            return text

        #  1) Удаляем всё, что в скобках, заменяя на один пробел
        cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", text)

        #  2) Удаляем ссылки вида [1], [2], [note 3]
        cleaned = re.sub(r"\s*\[[^\]]*\]\s*", " ", cleaned)

        #  3) Чистим повторяющиеся пробелы и лишние пробелы перед пунктуацией
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([.,;:?!])", r"\1", cleaned)

        #  4) Убираем случайные пробелы перед дефисами и после них
        cleaned = re.sub(r"\s*([-–—])\s*", r" \1 ", cleaned)

        #5) Убираем двойные пробелы, оставляем чистую строку
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

        return cleaned

    def execute_search(self, query: str):
        """
        Ищет статью по смыслу: использует OpenSearch API и парсит первый абзац,
        затем очищает абзац от скобочных вставок и ссылок.
        """
        try:
            search_url = "https://ru.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": query.strip(),
                "limit": 3,
                "namespace": 0,
                "format": "json"
            }

            response = requests.get(search_url, headers=self.headers, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()

            titles = data[1]
            links = data[3]

            if not titles:
                return "Ничего не найдено по запросу."

            title = titles[0]
            link = links[0]

            page = requests.get(link, headers=self.headers, timeout=8)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")

            # Иногда первый <p> может быть пустым — ищем первый ненулевой параграф
            first_p = None
            for p in soup.select("p"):
                txt = p.get_text(strip=True)
                if txt:
                    first_p = txt
                    break

            if not first_p:
                return f"Статья '{title}' найдена, но описание отсутствует."

            # Очистка текста (удаляем скобки, ссылки и т.д.)
            cleaned_text = self._clean_intro(first_p)

            return f"{cleaned_text} (Источник: {title})"

        except Exception as e:
            return f"Ошибка поиска: {e}"


# ------------------------
# Пример использования:
# ------------------------


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


class ToolCatcher:
    """
    Ловит теги <calc> и <search>.
    При <calc> вычисляет с CalcTool и сразу записывает в results.jsonl.
    """
    def __init__(self, calc_tool: CalcTool, output_file="results.jsonl"):
        self.calc_matches = []
        self.search_matches = []
        self.calc_tool = calc_tool
        self.output_file = output_file
        self.search_tool = ToolCatcherImprovedSearch()


    def catch(self, text: str):
        self.calc_matches = [m.strip() for m in re.findall(r"<calc>(.*?)</calc>", text, flags=re.DOTALL)]
        self.search_matches = [m.strip() for m in re.findall(r"<search>(.*?)</search>", text, flags=re.DOTALL)]

        # Выполняем скрипт для каждого <calc>
        with open(self.output_file, "a", encoding="utf-8") as f:
            for expr in self.calc_matches:
                result = self.calc_tool.calculate(expr)
                json_line = json.dumps({"expression": expr, "result": result}, ensure_ascii=False)
                f.write(json_line + "\n")
        
            for query in self.search_matches:
                    result = self.search_tool.execute_search(query)
                    json_line = json.dumps({"type": "search", "query": query, "result": result}, ensure_ascii=False)
                    f.write(json_line + "\n")
        return {"calc": self.calc_matches, "search": self.search_matches}

    def clear(self):
        self.calc_matches = []
        self.search_matches = []

    def __repr__(self):
        return f"<ToolCatcher: {len(self.calc_matches)} calc, {len(self.search_matches)} search>"


# main.py
if __name__ == "__main__":
    

    output = """Модель: <calc>3 + 2 = 5</calc>
    #Дополнительно: <search>президент Франции 2025</search>"""
    catcher = ToolCatcher(calc_tool=CalcTool())
    found = catcher.catch(output)

    print("Calc найдено:", found["calc"])        
    print("Search найдено:", found["search"])    

    # Очистка
    catcher.clear()
    print("После очистки:", catcher)
