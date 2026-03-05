import ollama
from PySide6.QtCore import QThread, Signal

class AIWorker(QThread):
    chunk_received = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            mensajes = [{"role": m["role"], "content": m["content"]} for m in self.messages]
            stream = ollama.chat(model="gemma3:4b", messages=mensajes, stream=True)
            for chunk in stream:
                text = chunk["message"]["content"]
                self.chunk_received.emit(text)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):

        self.quit()