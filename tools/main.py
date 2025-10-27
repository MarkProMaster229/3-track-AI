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

# Параметры генерации модели
MAX_NEW_TOKENS = 150
TEMPERATURE = 0.5
TOP_P = 0.5
DO_SAMPLE = True
TORCH_DTYPE = torch.float16
DEVICE_MAP = "auto"

# === Загружаем модель ===
print("Загружаю модель...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=TORCH_DTYPE,
    device_map=DEVICE_MAP
)
model.eval()

# === Инициализация тулов ===
catcher = ToolCatcher()
calc = CalcTool()
searcher = ToolCatcherImprovedSearch()
buffer = InstructionBuffer()

# === Вставка системной инструкции в JSONL ===
system_instruction = """Ты — ассистент.
Используй только теги <calc> для арифметики и <search> для поиска википедии.
Не выполняй лишние действия.
Отвечай кратко и по делу."""
with open(JSONL_PATH, "w", encoding="utf-8") as f:
    f.write(json.dumps({"text": system_instruction, "result": ""}, ensure_ascii=False) + "\n")

# === Функции ===
def generate_model_reply(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

def append_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def process_jsonl(file_path):
    """
    Прогоняет весь JSONL, ищет спецтеги и заменяет их на результаты тулов,
    возвращает список словарей с текстом и результатом.
    """
    updated_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            text = entry.get("text", "")

            # Ловим теги
            found = catcher.catch(text)

            # Инициализируем переменную результата
            final_result = text

            # Обрабатываем первый <calc>
            if found["calc"]:
                expr = found["calc"][0]
                calc_result = calc.calculate(expr)
                final_result = str(calc_result)
                text = re.sub(r"<calc>.*?</calc>", final_result, text, count=1)

            # Обрабатываем первый <search>
            elif found["search"]:
                query = found["search"][0]
                search_result = searcher.execute_search(query)
                final_result = search_result
                text = re.sub(r"<search>.*?</search>", final_result, text, count=1)

            # Удаляем все оставшиеся некорректные теги
            text = re.sub(r"<.*?>", "", text)

            catcher.clear()
            updated_lines.append({"text": text, "result": final_result})

    # Перезаписываем JSONL
    with open(file_path, "w", encoding="utf-8") as f:
        for line in updated_lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    return updated_lines

def format_final_answer(prompt, processed_entry):
    """
    Формирует текст в формате:
    Задача: ...
    Рассуждение: ...
    Ответ: ...
    """
    reasoning = f"Рассуждение: Обрабатываем задачу '{prompt.strip()}' с помощью инструментов."
    answer = processed_entry.get("result", "").strip()
    return f"Задача: {prompt.strip()}\n{reasoning}\nОтвет: {answer}"

# === Интерактивный цикл ===
print("Диалог с моделью. Введите 'exit' для выхода.\n")

while True:
    user_input = input("Вы: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # 1️⃣ Генерируем ответ модели
    model_output = generate_model_reply(user_input)
    append_jsonl(JSONL_PATH, {"text": model_output, "result": ""})
    print("Сырый ответ модели:", model_output)

    # 2️⃣ Прогоняем JSONL через тулзы
    updated_entries = process_jsonl(JSONL_PATH)

    # 3️⃣ Формируем финальный ответ с рассуждением
    final_entry = updated_entries[-1]
    formatted_text = format_final_answer(user_input, final_entry)
    print("После обработки тулов:", formatted_text)
    print("---")
