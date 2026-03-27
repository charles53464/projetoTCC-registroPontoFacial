from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

Window.size = (360, 600)

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Chama o construtor da classe Screen

        layout = MDBoxLayout(orientation="vertical")
        self.add_widget(layout)
        
        # Adiciona o widget de imagem
        self.image = Image()
        layout.add_widget(self.image)

    def load_video(self, *args):
        ret, frame = self.cap.read()  # Leitura do frame do OpenCV
        
        if not ret:
            print("Falha ao capturar o frame")
            return

        # Inverte a imagem (OpenCV usa BGR e Kivy espera a origem no canto inferior esquerdo)
        # Converte o frame para bytes para o buffer do Kivy
        buffer = cv2.flip(frame, 0).tobytes()
        
        # Cria a textura com as dimensões do frame (largura, altura)
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        
        # Preenche a textura com os dados do buffer
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        
        # Atualiza o widget de imagem com a nova textura
        self.image.texture = texture

    def open_camera_for_recognition(self):
        # Remove a mensagem (Opcional)
        for widget in self.children:
            if isinstance(widget, MDLabel):
                self.remove_widget(widget)
                
        # Iniciar captura de vídeo
        self.cap = cv2.VideoCapture(0)  # index 0
        
        if self.cap.isOpened():
            print("Mostrando a câmera")
            # Chama a função para carregar o vídeo
            Clock.schedule_interval(self.load_video, 1.0 / 60.0)
            print("Abriu a camera")
        else:
            print("Falha ao abrir a câmera")

class ScreenManagerApp(ScreenManager):
    def open_camera_for_recognition(self):
        # Chama o método de MainScreen para abrir a câmera
        self.get_screen('main').open_camera_for_recognition()

class MainApp(MDApp):
    def build(self):
        return Builder.load_string("""
ScreenManagerApp:
    MainScreen:
        name: "main"
        
        MDLabel:
            text: "Clique no botão para reconhecimento"
            halign: "center"
            theme_text_color: "Secondary"

        MDRaisedButton:
            text: "Iniciar Reconhecimento"
            size_hint: None, None
            size: "200dp", "50dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.1}
            on_press: root.open_camera_for_recognition()
""")

if __name__ == '__main__':
    MainApp().run()