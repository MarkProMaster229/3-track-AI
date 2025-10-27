# tool_catcher.py
import re

class ToolCatcher:
    """
    Универсальный ловец для тегов <calc> ... </calc> и <search> ... </search>.
    """
    def __init__(self):
        self.calc_matches = []
        self.search_matches = []

    def catch(self, text: str):
        """
        Ищет все вхождения <calc>...</calc> и <search>...</search>.
        Сохраняет их в соответствующие списки.
        :param text: текст вывода модели
        :return: словарь с результатами {'calc': [...], 'search': [...]}
        """
        self.calc_matches = re.findall(r"<calc>(.*?)</calc>", text, flags=re.DOTALL)
        self.search_matches = re.findall(r"<search>(.*?)</search>", text, flags=re.DOTALL)
        return {
            "calc": self.calc_matches,
            "search": self.search_matches
        }

    def clear(self):
        """
        Очищает все найденные записи.
        """
        self.calc_matches = []
        self.search_matches = []

    def __repr__(self):
        return f"<ToolCatcher: {len(self.calc_matches)} calc, {len(self.search_matches)} search>"

# main.py
#if __name__ == "__main__":
    #catcher = ToolCatcher()

    #output = """Модель: <calc>3 + 2 = 5</calc>
    #Дополнительно: <search>президент Франции 2025</search>"""

    #found = catcher.catch(output)

    #print("Calc найдено:", found["calc"])        # ['3 + 2 = 5']
    #print("Search найдено:", found["search"])    # ['президент Франции 2025']

    # Очистка
    #catcher.clear()
    #print("После очистки:", catcher)
