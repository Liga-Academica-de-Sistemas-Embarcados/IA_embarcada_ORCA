import threading

class UserInterface:
    def __init__(self):
        self.text = ""

    def start_prompt(self):
        self.thread = threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        while self.text != "stop":
            self.text = input("Prompt: ")

    def get(self):
        return self.text