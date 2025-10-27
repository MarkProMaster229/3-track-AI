import re
import requests
from bs4 import BeautifulSoup

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
if __name__ == "__main__":
    searcher = ToolCatcherImprovedSearch()

    tests = [
        "Эверест",
        "Альберт Эйнштейн",
        "Москва",
        "Эйнштеина",   # падеж/склонение
    ]

    for q in tests:
        print("\nЗапрос:", q)
        print(searcher.execute_search(q))
