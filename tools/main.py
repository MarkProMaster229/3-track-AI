import sys
import os
import json
import re

# Путь к папке с тулзами
sys.path.append(os.path.join(os.path.dirname(__file__), "tools"))

from tool_catcher import ToolCatcher
from calc_tool import CalcTool
from tool_catcher_improved_search import ToolCatcherImprovedSearch
from instruction_buffer import InstructionBuffer

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# === Настройки ===
MODEL_PATH = "/home/jovyan/finalModel"
JSONL_PATH = "model_output.jsonl"

# === Загружаем модель ===
print("Загружаю модель...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()

# === Инициализация тулов ===
catcher = ToolCatcher()
calc = CalcTool()
searcher = ToolCatcherImprovedSearch()

# === Функции ===
def generate_model_reply(prompt, max_new_tokens=150):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

def append_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def process_jsonl(file_path):
    """
    Прогоняет весь JSONL, ищет спецтеги и заменяет их на результаты тулов,
    оставляя только первый корректный результат и удаляя лишние.
    """
    updated_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            text = entry.get("text", "")

            # Ловим теги
            found = catcher.catch(text)

            # Обрабатываем первый <calc>, если есть
            if found["calc"]:
                expr = found["calc"][0]
                result = calc.calculate(expr)
                # Заменяем только первое вхождение тега на результат
                text = re.sub(r"<calc>.*?</calc>", str(result), text, count=1)

            # Обрабатываем первый <search>, если есть
            if found["search"]:
                query = found["search"][0]
                result = searcher.execute_search(query)
                # Заменяем только первое вхождение тега на результат
                text = re.sub(r"<search>.*?</search>", str(result), text, count=1)

            # Очищаем все оставшиеся некорректные теги
            text = re.sub(r"<.*?>", "", text)

            catcher.clear()
            updated_lines.append({"text": text})

    # Перезаписываем jsonl
    with open(file_path, "w", encoding="utf-8") as f:
        for line in updated_lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    return updated_lines

# === Интерактивный цикл ===
print("Диалог с моделью. Введите 'exit' для выхода.\n")

while True:
    user_input = input("Вы: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # 1️⃣ Генерируем ответ модели
    model_output = generate_model_reply(user_input)
    append_jsonl(JSONL_PATH, {"text": model_output})
    print("Сырый ответ модели:", model_output)

    # 2️⃣ Прогоняем JSONL через тулзы
    updated_entries = process_jsonl(JSONL_PATH)

    # 3️⃣ Берём последний (только что добавленный) ответ
    final_text = updated_entries[-1]["text"]
    print("После обработки тулов:", final_text)
    print("---")
