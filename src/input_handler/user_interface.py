import threading

class UserInterface:
    def __init__(self):
        self.text = ""
        self.stop_event = threading.Event()

    def start_prompt(self):
        self.thread = threading.Thread(target=self._read, daemon=True)
        self.thread.start()

    def _read(self):
        while not self.stop_event.is_set():
            self.text = input("Prompt: ").lower()
            if self.text == "stop":
                self.stop_event.set()
                break

    def get(self):
        return self.text

    def stop(self):
        self.stop_event.set()