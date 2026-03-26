import cv2
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from registro.models import Funcionario, Treinamento

class Command(BaseCommand):
    help = "Comando para teste de reconhecimento facial com exibição ao vivo da câmera"

    def handle(self, *args, **kwargs):
        self.reconhecer_faces()

    def reconhecer_faces(self):
        # Carregamento do classificador Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Correção: Adicionado () ao final do create
        reconhecedor = cv2.face.EigenFaceRecognizer_create()
        
        # Carregar o modelo de treinamento
        treinamento = Treinamento.objects.last() # Pega o treinamento mais recente
        
        if not treinamento:
            self.stdout.write(self.style.ERROR("Modelo de treinamento não encontrado."))
            return
            
        model_path = os.path.join(settings.MEDIA_ROOT, treinamento.modelo.name)
        
        if not os.path.exists(model_path):
            self.stdout.write(self.style.ERROR(f"Arquivo não encontrado: {model_path}"))
            return

        reconhecedor.read(model_path)

        # CAP_DSHOW resolve problemas de abertura de câmera no Windows
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        largura, altura = 220, 220
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL

        self.stdout.write(self.style.SUCCESS("Iniciando câmera... Pressione 'q' para sair."))

        while True:
            ret, frame = camera.read()
            if not ret:
                print("Erro ao acessar a câmera.")
                break

            frame_redimensionado = cv2.resize(frame, (480, 360))
            imagemCinza = cv2.cvtColor(frame_redimensionado, cv2.COLOR_BGR2GRAY)
            
            # Correção: minNeighbors escrito corretamente
            faces_detectadas = face_cascade.detectMultiScale(
                imagemCinza, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            for (x, y, l, a) in faces_detectadas:
                imagemFace = cv2.resize(imagemCinza[y:y+a, x:x+l], (largura, altura))
                cv2.rectangle(frame_redimensionado, (x, y), (x + l, y + a), (0, 255, 0), 2)
                
                label, confianca = reconhecedor.predict(imagemFace)
                
                # Tratamento de erro caso o ID não exista no banco de dados
                try:
                    funcionario = Funcionario.objects.get(id=label)
                    # No EigenFaces, quanto menor o valor de confiança, maior a precisão
                    if confianca < 5000:
                        nome_exibicao = str(funcionario.nome).split()[0]
                    else:
                        nome_exibicao = "Desconhecido"
                except Funcionario.DoesNotExist:
                    nome_exibicao = "ID Inexistente"

                # Correção: cv2.putText precisa de coordenadas e cor
                cv2.putText(
                    frame_redimensionado, 
                    nome_exibicao, 
                    (x, y - 10), 
                    font, 
                    1, 
                    (0, 255, 0), 
                    2
                )
            
            cv2.imshow("Reconhecimento Facial", frame_redimensionado)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        camera.release()
        cv2.destroyAllWindows()