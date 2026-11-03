from dataclasses import dataclass
from receiver import Receiver
from user_interface import UserInterface
import numpy as np

class Factory:
    def __init__(self, recieve, interface):
        self.recieve = recieve
        self.interface = interface
        self.prompt = ""
        self.frame = None

    def build(self):
        ok, frame = self.recieve.capture()

        if not ok:
            return False

        self.frame = frame
        self.prompt = self.interface.get()
        return True

prompt = UserInterface()
prompt.start_prompt()

cam = Receiver()
InputObj = Factory(cam, prompt)

while InputObj.build():
    if InputObj.prompt:
        # Direcinamneto para método Arm Client
        pass
    if not cam.show(InputObj.frame):
        break

cam.release_cam()