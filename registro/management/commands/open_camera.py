from django.core.management.base import BaseCommand
import cv2


class Command(BaseCommand):
    help = 'Abre a câmera e exibe o vídeo em tempo real'

    def handle(self, *args, **kwargs):
        # Abre a câmera (0 é o índice padrão)
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.stdout.write(self.style.ERROR('Erro ao abrir a câmera'))
            return

        self.stdout.write(
            self.style.SUCCESS('Câmera aberta com sucesso. Pressione "ESC" para sair.')
        )

        while True:
            # Captura frame por frame
            ret, frame = cap.read()

            if not ret:
                self.stdout.write(self.style.ERROR('Erro ao capturar o frame'))
                break

            # Exibe o frame
            cv2.imshow('Camera', frame)

            # Captura tecla pressionada
            key = cv2.waitKey(1) & 0xFF

            # Sai do loop ao pressionar ESC (código 27)
            if key == 27:
                break

        # Libera a câmera e fecha as janelas
        cap.release()
        cv2.destroyAllWindows()

        self.stdout.write(self.style.SUCCESS('Câmera fechada.'))