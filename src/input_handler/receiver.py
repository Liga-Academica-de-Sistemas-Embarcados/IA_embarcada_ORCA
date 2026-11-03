import cv2

class Receiver:

    def __init__(self,indice = 0):
        self.cam = cv2.VideoCapture(indice)

    def capture(self):
        ok, frame = self.cam.read()

        if ok:
            frame = cv2.flip(frame, 1)
        return ok, frame

    def show(self, frame):
        cv2.imshow("cam", frame)
        return cv2.waitKey(1) != 27

    def release_cam(self):
        self.cam.release()
        cv2.destroyAllWindows()