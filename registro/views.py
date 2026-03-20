import cv2
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse
from .forms import FuncionarioForm, ColetaFacesForm
from .models import Funcionario, ColetaFaces
from registro.camera import VideoCamera

# Instância única da câmera
camera_detection = VideoCamera()

def gen_detect_face(camera):
    while True:
        frame = camera.detect_face()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def face_detection(request):
    """Gera o streaming de vídeo para o template"""
    return StreamingHttpResponse(
        gen_detect_face(camera_detection),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def criar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            funcionario = form.save()
            return redirect('criar_coleta_faces', funcionario_id=funcionario.id)
    else:
        form = FuncionarioForm()
    return render(request, 'criar_funcionario.html', {'form': form})

def criar_coleta_faces(request, funcionario_id):
    funcionario = Funcionario.objects.get(id=funcionario_id)
    botao_clicado = request.GET.get('clicked', 'False') == 'True'
    
    context = {
        'funcionario': funcionario,
        'face_detection': face_detection,
        'valor_botao': botao_clicado,
    }
    
    if botao_clicado:
        # Chama a função de extração
        context = face_extract(context, funcionario) 
        
    return render(request, 'criar_coleta_faces.html', context)


# Cria uma função para extrair e retornar os caminhos das imagens
def extract(camera_detection, funcionario_slug):
    amostra = 0  # Contador de amostras
    numeroAmostras = 10  # Número de amostras
    largura, altura = 220, 220
    file_paths = []

    while amostra < numeroAmostras:
        # Captura frame da câmera
        ret, frame = camera_detection.get_camera()

        if not ret:
            print("Erro ao capturar frame")
            continue

        # Captura face
        crop = camera_detection.sample_faces(frame)

        if crop is not None:
            amostra += 1

            # Resize + escala de cinza
            face = cv2.resize(crop, (largura, altura))
            imagemCinza = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Caminho do arquivo
            file_name_path = f'./tmp/{funcionario_slug}_{amostra}.jpg'

            # Salva imagem
            cv2.imwrite(file_name_path, imagemCinza)
            file_paths.append(file_name_path)
        else:
            print("Face não encontrada")

    # Reinicia a câmera após capturas
    camera_detection.restart()

    return file_paths


def face_extract(context, funcionario):
    num_coletas = ColetaFaces.objects.filter(funcionario__slug=funcionario.slug).count()
    if num_coletas >= 10:
        context['erro'] = 'Limite máximo de coletas atingido.'
    else:
        files_paths = extract(camera_detection, funcionario.slug) # Captura faces e retorna paths
        for path in files_paths:
            # Cria uma instância de ColetaFaces e salva a imagem
            coleta_face = ColetaFaces.objects.create(funcionario=funcionario)
            coleta_face.image.save(os.path.basename(path), open(path, 'rb'))
            os.remove(path) # Remove o arquivo temporário após o salvamento
            
        # Atualiza o contexto com as coletas salvas
        context['file_paths'] = ColetaFaces.objects.filter(funcionario__slug=funcionario.slug)
        context['extracao_ok'] = True # Define sinalizador de sucesso
        
    return context