class InstructionBuffer:
    """
    Класс для хранения последовательности инструкций для модели.
    """
    def __init__(self):
        # Здесь храним инструкции в виде списка
        self.instructions = []

    def add_instruction(self, instruction: str):
        """
        Добавляет инструкцию в буфер.
        :param instruction: строка с инструкцией
        """
        self.instructions.append(instruction)

    def get_all_instructions(self) -> str:
        """
        Возвращает все инструкции в виде одной строки,
        объединяя их через '\n'.
        """
        return "\n".join(self.instructions)

    def clear(self):
        """
        Очищает буфер инструкций.
        """
        self.instructions = []

    def __len__(self):
        """
        Возвращает количество инструкций в буфере.
        """
        return len(self.instructions)

    def __repr__(self):
        return f"<InstructionBuffer {len(self.instructions)} instructions>"


#main.py
#buffer = InstructionBuffer()

#buffer.add_instruction("Скажи привет пользователю.")
#buffer.add_instruction("Выведи текущее время.")

#print(buffer.get_all_instructions())
# Выведет:
# Скажи привет пользователю.
# Выведи текущее время.

#print(len(buffer))  # 2
#buffer.clear()
#print(len(buffer))  # 0