import cv2
import os


class VideoCamera(object):

    def __init__(self):
        # Abertura da câmera (0 = câmera padrão)
        self.video = cv2.VideoCapture(0)

        # Verifica se a câmera foi aberta corretamente
        if not self.video.isOpened():
            print("Erro ao acessar a câmera.")

    def __del__(self):
        # Libera a câmera ao destruir a classe
        self.video.release()

    def restart(self):
        # Reinicia a câmera
        self.video.release()
        self.video = cv2.VideoCapture(0)

    def get_camera(self):
        # Leitura do frame
        ret, frame = self.video.read()

        # Verifica se a captura foi bem-sucedida
        if not ret:
            print("Falha ao capturar o frame.")
            return None

        # Converte o frame para JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Retorna em bytes (necessário para streaming no Django)
        return jpeg.tobytes()