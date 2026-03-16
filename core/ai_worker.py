import ollama
from PySide6.QtCore import QThread, Signal
from config import OLLAMA_MODEL, OLLAMA_MAX_TOKENS

class AIWorker(QThread):
    chunk_received = Signal(str)
    completed = Signal()
    error = Signal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def run(self):
        try:
            mensajes = [{"role": m["role"], "content": m["content"]} for m in self.messages]
            stream = ollama.chat(model=OLLAMA_MODEL, messages=mensajes, stream=True, options={"num_predict": OLLAMA_MAX_TOKENS})
            for chunk in stream:
                if self._stop_requested:
                    return
                text = chunk["message"]["content"]
                self.chunk_received.emit(text)
            self.completed.emit()
        except Exception as e:
            if not self._stop_requested:
                self.error.emit(str(e))