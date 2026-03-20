import cv2
import os

class VideoCamera:
    def __init__(self):
        # Carrega o classificador de face padrão do OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Inicia a webcam
        self.video = cv2.VideoCapture(0)
        self.img_dir = "./tmp"

        self.capturado = False
        
        # Garanta que o diretório tmp seja criado
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

    def __del__(self):
        self.video.release()

    def restart(self):
        """Reinicia a captura da câmera para limpar o buffer"""
        self.video.release()
        self.video = cv2.VideoCapture(0)

    def get_camera(self):
        """Retorna o status e o frame atual da câmera"""
        ret, frame = self.video.read()
        if not ret:
            print("falha ao capturar o frame")
            return False, None
        return True, frame

    def detect_face(self):
        ret, frame = self.get_camera()
        if not ret or frame is None:
            return None
        
        altura, largura, _ = frame.shape
        centro_x, centro_y = int(largura/2), int(altura/2)

        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b

        # Limites
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(largura, x2), min(altura, y2)

        roi = frame[y1:y2, x1:x2]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray_roi,
            scaleFactor=1.1,
            minNeighbors=5
        )

        cor = (0, 0, 255)
        if len(faces) > 0:
            cor = (0, 255, 0)

        cv2.ellipse(
            frame,
            (centro_x, centro_y),
            (a, b),
            0, 0, 360,
            cor,
            3
        )

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def sample_faces(self, frame):
        if frame is None:
            return None

        altura, largura, _ = frame.shape
        centro_x, centro_y = int(largura/2), int(altura/2)

        a, b = 140, 180
        x1, y1 = max(0, centro_x - a), max(0, centro_y - b)
        x2, y2 = min(largura, centro_x + a), min(altura, centro_y + b)

        roi = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        for (x, y, w, h) in faces:
            # RECORTE CORRETO (dentro da ROI)
            cropped_face = roi[y:y+h, x:x+w]

            self.capturado = True
            return cropped_face

        return None