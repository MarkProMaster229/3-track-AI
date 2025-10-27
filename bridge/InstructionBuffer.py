class InstructionBuffer:
    def __init__(self):
        self.instructions = []

    def add(self, instruction: str):
        """
        Добавляет инструкцию в буфер.
        instruction: строка с обязательными токенами или инструкцией
        """
        self.instructions.append(instruction)

    def __repr__(self):
        return f"<InstructionBuffer: {len(self.instructions)} instructions>"
    
    
    
#main.py

#from instruction_buffer import InstructionBuffer

#buffer = InstructionBuffer()

# добавляем инструкции в буфер
#buffer.add("""Вопрос: "Ваня купил 3 яблока, а потом ещё 2. Сколько всего?"
#Ответ: "<calc>3+2=5</calc>\""")

#buffer.add("""Вопрос: "Кто президент Франции в 2025?"
#Ответ: "<search>президент Франции 2025</search>\""")

#buffer.add("""Вопрос: "У Пети 2 яблока, у Вани на 2 яблока больше. Сколько яблок у Вани?"
#Ответ: """)  # сюда модель подставит ответ

# печатаем содержимое буфера
#print(buffer.instructions)