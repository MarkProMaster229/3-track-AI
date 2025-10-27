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

#buffer = InstructionBuffer()
#buffer.add("Скажи привет пользователю.")  # добавляем инструкцию
#buffer.add("Выведи текущее время.")      # добавляем ещё одну

#print(buffer.instructions)
# ['Скажи привет пользователю.', 'Выведи текущее время.']
