# tool_catcher.py
import re
import json

from tools.search import ToolCatcherImprovedSearch
from tools.calc  import CalcTool
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
    catcher = ToolCatcher()

    output = """Модель: <calc>3 + 2 = 5</calc>
    #Дополнительно: <search>президент Франции 2025</search>"""

    found = catcher.catch(output)

    print("Calc найдено:", found["calc"])        
    print("Search найдено:", found["search"])    

    # Очистка
    catcher.clear()
    print("После очистки:", catcher)
