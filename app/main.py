import cv2
import tempfile
import requests
import os
from datetime import datetime

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivymd.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

Window.size = (340, 680)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Chama o construtor da classe Screen
        self.recognized_user = None  # Retorna usuário
        self.recognized = False  # status do reconhecimento
        self.recognition_enabled = False  # Variável para controlar o início 

        layout = MDBoxLayout(
            orientation="vertical",
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        ) 
        self.add_widget(layout)  # Adiciona o layout à tela

        # Adiciona o widget de imagem
        self.image = Image()
        layout.add_widget(self.image)

        tmp_dir = "./tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        # Carrega o classificador frontal do OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            "./lib/haarcascade_frontalface_default.xml"
        )
        self.reconhecedor = cv2.face.EigenFaceRecognizer_create()

        # Baixa o modelo de treinamento e carrega no reconhecedor
        treinamento = requests.get(
            "http://127.0.0.1:8000/api/treinamento/"
        ).json()

        model_url = treinamento[0]['modelo']  # Pega o primeiro item da lista

        # Caminho do arquivo temporário no diretório local
        tmp_path = os.path.join(tmp_dir, "modelo.xml")

        # Salva o modelo no diretório tmp
        with open(tmp_path, "wb") as temp_file:
            temp_file.write(requests.get(model_url).content)
            self.reconhecedor.read(temp_file.name) # Carrega o modelo no reconhecedor


    def load_video(self, *args):

        ret, frame = self.cap.read()

        if not ret or frame is None:
            print("Falha ao capturar frame")
            return

        # dimensões
        altura, largura, _ = frame.shape
        centro_x, centro_y = largura // 2, altura // 2
        a, b = 140, 180
        x1, y1 = centro_x - a, centro_y - b
        x2, y2 = centro_x + a, centro_y + b

        cv2.ellipse(frame, (centro_x, centro_y), (a, b), 0, 0, 360, (144, 238, 144), 5)

        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        self.image.texture = texture

        if not self.recognition_enabled:
            return
        
        roi = frame[y1:y2, x1:x2]

        imagemCinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        facesDetectadas = self.face_cascade.detectMultiScale(imagemCinza, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in facesDetectadas:
            imagemFace = cv2.resize(imagemCinza[y:y+h, x:x+w], (220, 220))

            label, confianca = self.reconhecedor.predict(imagemFace)
            print(f"ID reconhecido: {label}")

            if label:
                response = requests.get(f"http://127.0.0.1:8000/api/funcionarios/{label}/")
                if response.status_code == 200: # retorno é OK
                    funcionario = response.json()
                    self.show_recognized_user(funcionario)
                    
                    Clock.unschedule(self.load_video)  # Para de atualizar o vídeo
                    self.reset_camera()  # Limpa a câmera
                    break  # Sai do loop após reconhecer um usuário
                       

    def reset_camera(self):
        self.ids.headimage.opacity = 1

        if self.cap:
            self.cap.release()
            self.image.texture = None
        
    def open_camera_for_recognition(self):

       self.ids.headimage.opacity = 0

       for widget in self.children:
            if isinstance(widget, MDLabel):
                self.remove_widget(widget)

            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                print("câmera aberta")
                Clock.schedule_interval(self.load_video, 1.0 / 60.0)
                Clock.schedule_once(self.start_recognition, 5)  

            else:
                print("falha ao abrir a câmera")    

    def start_recognition(self, *args):
        # Ativa o reconhecimento após o tempo de espera
        self.recognition_enabled = True

    def show_recognized_user(self, funcionario):
        print(funcionario)
        self.manager.current = 'usuario'

        usuario_screen = self.manager.get_screen('usuario')
        usuario_screen.ids.foto.source = funcionario["foto"]
        usuario_screen.ids.nome.text = f"Nome: {funcionario['nome']}"
        usuario_screen.ids.cpf.text = f"CPF: {funcionario['cpf']}"
        usuario_screen.ids.data_hora.text = f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        usuario_screen.funcionario_id = funcionario["id"]
        usuario_screen.data_hora = datetime.now().isoformat()


        usuario_screen.ids.card.opacity = 1


class UsuarioScreen(MDScreen):

    def confirmar_registro(self):
        if not self.funcionario_id:
            print("Funcionário não definido.")
            return

        funcionario = {
            "funcionario": self.funcionario_id,  # Envia o ID para API
            "data_hora": self.data_hora  # Data
        }
        print(funcionario)
        url_api = "http://127.0.0.1:8000/api/registros/"

        try:
            response = requests.post(url_api, json=funcionario)

            if response.status_code == 201:
                print("Registro salvo com sucesso!")

               # Mensagem de sucesso
                comprovante_screen = self.manager.get_screen('comprovante')

                mensagem = (
                    f"Matricula: {self.funcionario_id}\n"
                    f"{self.ids.data_hora.text}\n"
                )

                comprovante_screen.ids.comprovante_label.text = mensagem

                # Navegar para a tela de comprovante
                self.manager.current = 'comprovante'
            else:
                print("Erro ao salvar registro:", response.json())

        except Exception as e:
            print("Erro na conexão com a API:", e)
        pass


class ComprovanteScreen(MDScreen):
    pass


class ScreenManagerApp(ScreenManager):
 def open_camera_for_recognition(self):
 # Chama o método de MainScreen para abrir a câmera
    self.get_screen('main').open_camera_for_recognition() 


class MainApp(MDApp):
    def build(self):
        return Builder.load_string("""
ScreenManagerApp:
    MainScreen:
    UsuarioScreen:
    ComprovanteScreen:
        
<MainScreen>:
    name: "main"
    MDScreen:
        MDTopAppBar:
            title: "Reconhecimento"
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.173, 0.243, 0.314, 1
            elevation: 0.5
            pos_hint: {"top": 1}
        MDBoxLayout:
            orientation: "vertical"
            adaptive_size: True
            spacing: "20dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            MDCard:
                id: headimage
                size_hint: None, None
                size: "300dp", "300dp"
                pos_hint: {"center_x": 0.5}
                AsyncImage:
                    size_hint: (1, 1)
                    pos_hint: {'center_x': 0.5}
                    source: './assets/teste.jpg'
        MDRaisedButton:
            text: 'Registrar'
            font_size: '20sp'
            pos_hint: {'center_x': 0.5, 'center_y': 0.25}
            md_bg_color: 1, 0.388, 0.278, 1
            size_hint: (0.7, 0.1)
            elevation: 0.5
            on_press: root.open_camera_for_recognition()

<UsuarioScreen>:
    name: "usuario"
    MDScreen:
        md_bg_color: 0.941, 0.957, 0.973, 1
        MDTopAppBar:
            title: "Usuário Identificado"
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.173, 0.243, 0.314, 1
            elevation: 0.5
            pos_hint: {"top": 1}
        MDCard:
            id: card
            size_hint: None, None
            size: "280dp", "300dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            opacity: 0
            BoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                AsyncImage:
                    id: foto
                    size_hint: (1, 0.5)
                    pos_hint: {"center_x": 0.5}
                MDLabel:
                    id: nome
                    adaptive_size: True
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    pos_hint: {"center_x": .5, "center_y": .5}
                    padding: "4dp", "4dp"
                MDLabel:
                    id: cpf
                    adaptive_size: True
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    pos_hint: {"center_x": .5, "center_y": .5}
                    padding: "4dp", "4dp"
                MDLabel:
                    id: data_hora
                    adaptive_size: True
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    pos_hint: {"center_x": .5, "center_y": .5}
                    padding: "4dp", "4dp"
        MDRaisedButton:
            text: 'Confirmar'
            font_size: '20sp'
            pos_hint: {'center_x': 0.5, 'center_y': 0.25}
            size_hint: (0.7, 0.1)
            elevation: 0.5
            md_bg_color: 0.298, 0.686, 0.314, 1
            on_press: root.confirmar_registro()
        MDRaisedButton:
            text: 'Não sou eu'
            font_size: '20sp'
            pos_hint: {'center_x': 0.5, 'center_y': 0.1}
            size_hint: (0.7, 0.1)
            elevation: 0.5
            md_bg_color: 0.9, 0.3, 0.3, 1
            on_press: 
                root.manager.current = 'main'
                root.manager.get_screen('main').reset_camera()

<ComprovanteScreen>:
    name: "comprovante"
    MDScreen:
        md_bg_color: 0.941, 0.957, 0.973, 1
        MDTopAppBar:
            title: "Comprovante"
            specific_text_color: 1, 1, 1, 1
            anchor_title: "center"
            md_bg_color: 0.173, 0.243, 0.314, 1
            elevation: 0.5
            pos_hint: {"top": 1}
        MDCard:
            id: card_comprovante
            size_hint: None, None
            size: "280dp", "300dp"
            md_bg_color: 1.0, 0.976, 0.912, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            opacity: 1
            BoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                MDLabel:
                    id: comprovante_label
                    text: 'Comprovante'
                    halign: 'center'
                    theme_text_color: "Primary"
                    font_style: "H6"
        MDRaisedButton:
            text: 'Fechar'
            font_size: '20sp'
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            md_bg_color: 1, 0.388, 0.278, 1
            size_hint: (0.7, 0.1)
            elevation: 0.5
            on_press: 
                root.manager.current = 'main'
                root.manager.get_screen('main').reset_camera()
    """)


if __name__ == '__main__':
    MainApp().run()