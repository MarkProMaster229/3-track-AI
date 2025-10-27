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

    def execute_search(self, query: str):
        """
        Ищет статью по смыслу: исправляет окончания, ищет через API и парсит первый абзац.
        """
        try:
            # --- 1️⃣ Поиск похожих статей через OpenSearch API ---
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

            first_p = soup.select_one("p")
            if not first_p:
                return f" Статья '{title}' найдена, но описание отсутствует."

            text = first_p.get_text(strip=True)
            return f"{text} (Источник: {title})"

        except Exception as e:
            return f"Ошибка поиска: {e}"
        
searcher = ToolCatcherImprovedSearch()

print(searcher.execute_search("Автомобилаь"))