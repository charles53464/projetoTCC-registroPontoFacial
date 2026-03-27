import cv2
import numpy as np

# Defina os parâmetros da imagem (Canvas Vertical)
altura, largura = 480, 360
frame = np.zeros((altura, largura, 3), dtype=np.uint8)  # Criando imagem preta

# Defina os parâmetros do quadrado
lado = 200  # Comprimento do lado
centro_x, centro_y = int(largura / 2), int(altura / 3)

# Cálculo das coordenadas (Canto superior esquerdo e inferior direito)
top_left = (centro_x - lado // 2, centro_y - lado // 2)
bottom_right = (centro_x + lado // 2, centro_y + lado // 1)

# Cor Verde claro (Formato BGR)
cor = (144, 238, 144) 

# Desenhe o quadrado
# Parâmetros: imagem, ponto1, ponto2, cor, espessura
cv2.rectangle(frame, top_left, bottom_right, cor, 23)

# Exiba a imagem
cv2.imshow("Quadrado Verde Claro", frame)

# Finalização
cv2.waitKey(0)
cv2.destroyAllWindows()