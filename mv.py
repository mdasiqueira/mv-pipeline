import cv2
import numpy as np
import base64
import traceback

class Camera:

    def __init__(self):
        self.camera = None
        self.connected = False
        self.enabled = True
        self.success = False
        self.camera_channel = 0
        self.camera_exposure_us = 12000
        self.output_var = "cam_frame_out"
        self.frame = None


    def connect(self):
        if self.enabled:
            try:
                self.camera = cv2.VideoCapture(self.camera_channel)
                self.connected = True
                print("Vídeo estabelecido com sucesso")
            except:
                self.connected = False
                print("Vídeo estabelecido: não")
        else:
            self.connected = False
    def disconnect(self):
        if self.connected:
            try:
                self.camera.release()
                self.camera = None
                self.connected = False
                print("Vídeo desconectado.")
            except:
                self.connected = False
                print("Vídeo estabelecido: não")
        else:
            self.connected = False

    def read(self):
        result = self.frame
        if self.enabled:
            try:
                if not self.connected:
                    self.connect()
                if self.connected:
                    ret, self.frame = self.camera.read()
                    result = self.frame
                    self.success = True
            except:
                self.success = False
        else:
            if self.connected:
                self.disconnect()
        return result

class Crop:

    def __init__(self):
        self.enabled = False
        self.x = 0
        self.y = 0
        self.dx = 500
        self.dy = 500
        self.output = 'frame'

    def crop(self, img):
        result = img
        if self.enabled:
            h, w, channels = img.shape
            if self.x + self.dx > w:
                self.dx = w - self.x
            if self.y + self.dy > h:
                self.dy = h - self.y
            if hasattr(img, 'shape'):
                frame_cropped = img[self.y: (self.y + self.dy), self.x:(self.x+self.dx)]
                result = frame_cropped
        return result

class SubstractBackground:

    def __init__(self):
        self.enabled = False
        self.previus_img = 'last_frame'
        self.current_img = 'frame'
        self.output = 'frame'
        self.mog2_bgsub = None

    def subtractBackground_MV(self, img_current, img_last):
        result = img_current
        if self.enabled:
            if hasattr(img_current, 'shape') and hasattr(img_last, 'shape'):
                print("img_curr.shape = ", img_current.shape)
                print("img_last.shape = ", img_last.shape)
                if img_current.shape == img_last.shape:
                    img_subbed = cv2.subtract(img_current, img_last)
                    result = img_subbed
                else:
                    print("As imagens para subtração não são do mesmo tipo.")
        return result

    def subtractBackground(self, img_current, mog2_bgsub):
        result = img_current
        if self.enabled:
            if hasattr(img_current, 'shape'):
                fgmask = mog2_bgsub.apply(img_current)
                result = fgmask
        return result

class Binarize:

    def __init__(self):
        self.enabled = False
        self.r = 0.3
        self.g = 0.3
        self.b = 0.3
        self.k = 128

    def binarize(self, img):
        # Out[i, j] = (Input[i, j, 0] * r + Input[i, j, 1] * g + Input[i, j, 2] * b) > k
        result = img
        try:
            if self.enabled:
                if hasattr(img, 'shape'):
                    h, w, channels = img.shape
                    if channels >= 3:
                        bin_img = np.zeros([h, w, 1], dtype=np.uint8)
                        for i in range(0, w):
                            for j in range(0, h):
                                fill_pixel = (img[j, i, 0]*self.r + img[j, i, 1]*self.g + img[j, i, 0]*self.b) > self.k
                                bin_img[j, i] = 255 if fill_pixel else 0
                result = bin_img
        except:
            pass
        return result

class DetectFaces:

    def __init__(self):
        self.enabled = True
        self.box_color = (0, 255, 0)
        self.face_cascade = None

    def detectFaces(self, img):

        result = img
        if self.enabled:
            if self.face_cascade == None:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            if hasattr(img, 'shape'):
                try:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        img = cv2.rectangle(img, (x, y), (x + w, y + h), self.box_color, 1)
                    result = img
                except:
                    traceback.print_exc()
                    print("Falha no Face Detection")
                    pass
        return result


class Streammer:

    def __init__(self):
        self.enabled = True
        self.frame = None
        self.waiting_image = cv2.imread(filename='images/no-signal.png')

    def stream(self, img):
        try:
            if hasattr(img, 'shape'):
                if self.enabled:
                    self.frame = img
                else:
                    self.frame = self.waiting_image
        except:
            self.frame = self.waiting_image

    def gen(self):
        try:
            while True:
                f = self.frame if (self.frame is not None) else self.waiting_image
                ret, buffer = cv2.imencode('.jpg', f)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print("Erro no generator:\n", e)
            traceback.print_exc()

class Lambda:

    def __init__(self):
        # Implementado pelo lambda:
        # self.code = "frame = faceDetector.detectFaces(img=frame)"
        self.enabled = False
        self.code = "print('Hello From Lambda Code')"

    def setCodeB64(self, code_b64):

        code_b64_bytes = code_b64.encode('ascii')
        code_plain_bytes = base64.b64decode(code_b64_bytes)
        code_plain = code_plain_bytes.decode('ascii')
        self.code = code_plain
        print("Código lambda atualizado: ", code_plain)