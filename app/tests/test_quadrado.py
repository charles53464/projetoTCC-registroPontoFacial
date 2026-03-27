import cv2
import numpy as np

# Defina os parâmetros da imagem (Proporção vertical 480x360)
altura, largura = 480, 360
frame = np.zeros((altura, largura, 3), dtype=np.uint8)  # Criando o canvas preto

# Defina os parâmetros do quadrado
lado = 140  # Comprimento de cada lado
centro_x, centro_y = int(largura / 2), int(altura / 2)

# Cálculo das coordenadas dos vértices (Superior Esquerdo e Inferior Direito)
top_left = (centro_x - lado // 2, centro_y - lado // 2)
bottom_right = (centro_x + lado // 2, centro_y + lado // 2)

# Cor Verde claro (Formato BGR: Blue=144, Green=238, Red=144)
cor = (144, 238, 144) 

# Desenhe o quadrado (cv2.rectangle utiliza os dois pontos opostos)s233
cv2.rectangle(frame, top_left, bottom_right, cor, 2)

# Exiba a imagem
cv2.imshow("Quadrado Verde Claro", frame)

# Finalização
cv2.waitKey(0)
cv2.destroyAllWindows()