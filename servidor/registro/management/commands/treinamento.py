import os
import numpy as np
import cv2
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from registro.models import ColetaFaces, Treinamento

class Command(BaseCommand):
    help = "Treina o classificador Eigen para reconhecimento facial"

    def handle(self, *args, **kwargs):
        self.treinamento_face()

    def treinamento_face(self):
        self.stdout.write(self.style.WARNING("Iniciando treinamento com a base de dados..."))
        
        # 1. REMOVIDO threshold=0 (Padrão do OpenCV é melhor para começar)
        eigenFace = cv2.face.EigenFaceRecognizer_create(num_components=50)

        faces, labels = [], []
        erro_count = 0

        # Processa cada imagem em ColetaFaces
        for coleta in ColetaFaces.objects.all():
            # Melhor forma de pegar o caminho no Django: .path
            image_path = coleta.image.path 

            if not os.path.exists(image_path):
                print(f"Caminho não encontrado: {image_path}")
                erro_count += 1
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f"Erro ao carregar a imagem: {image_path}")
                erro_count += 1
                continue

            imagemFace = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            imagemFace = cv2.resize(imagemFace, (220, 220))
            faces.append(imagemFace)
            labels.append(coleta.funcionario.id)

        if not faces:
            self.stdout.write(self.style.ERROR("Nenhuma face encontrada para treinamento."))
            return

        try:
            # Realiza o treinamento
            eigenFace.train(np.array(faces), np.array(labels))
            print(f"{len(faces)} imagens treinadas com sucesso.")
            
            # 2. CAMINHO PARA WINDOWS (Usa a pasta MEDIA temporariamente)
            # Criamos o caminho absoluto para evitar erro de permissão
            media_path = os.path.abspath(settings.MEDIA_ROOT)
            if not os.path.exists(media_path):
                os.makedirs(media_path)
                
            model_filename = os.path.join(media_path, "classificadorEigen.yml")
            
            # 3. GRAVAÇÃO NO DISCO
            eigenFace.write(model_filename)
            
            # 4. SALVA NO BANCO DE DADOS
            if os.path.exists(model_filename):
                with open(model_filename, 'rb') as f:
                    # Sempre usa o ID 1 para atualizar o mesmo registro de treinamento
                    treinamento, created = Treinamento.objects.get_or_create(id=1)
                    treinamento.modelo.save('classificadorEigen.yml', File(f), save=True)
                
                # 5. LIMPEZA (Fecha o arquivo antes de deletar)
                try:
                    os.remove(model_filename)
                except:
                    pass

            self.stdout.write(self.style.SUCCESS(f"Imagens com erro no carregamento: {erro_count}"))
            self.stdout.write(self.style.SUCCESS("TREINAMENTO EFETUADO COM SUCESSO"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro durante o treinamento: {e}"))