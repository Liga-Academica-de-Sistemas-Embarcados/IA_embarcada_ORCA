import threading
import time
import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

def nada(x):
    pass

# =========================================================================
# 1. CONFIGURAÇÃO DA IA OTIMIZADA PARA VELOCIDADE
# =========================================================================
print("Carregando Depth Anything V2 Small...")
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype_ia = torch.float16 if device == "cuda" else torch.float32
modelo_id = "depth-anything/Depth-Anything-V2-Small-hf"

processor = AutoImageProcessor.from_pretrained(modelo_id)
processor.size = {"height": 196, "width": 252}

model = AutoModelForDepthEstimation.from_pretrained(
    modelo_id, torch_dtype=dtype_ia
).to(device).eval()
print(f"Modelo pronto em: {device.upper()} ({dtype_ia})")

# =========================================================================
# 2. VARIÁVEIS COMPARTILHADAS (MULTITHREADING + FPS DA IA)
# =========================================================================
frame_para_ia = None
mapa_prof_bruto = None
fps_ia = 0.0
trava_thread = threading.Lock()
rodando = True

def trabalhador_ia():
    """Roda a estimativa de profundidade em segundo plano e mede o FPS da IA."""
    global frame_para_ia, mapa_prof_bruto, fps_ia, rodando
    while rodando:
        with trava_thread:
            if frame_para_ia is None:
                img_local = None
            else:
                img_local = frame_para_ia.copy()
                frame_para_ia = None

        if img_local is None:
            time.sleep(0.005)
            continue

        t_inicio_ia = time.perf_counter()

        img_pil = Image.fromarray(cv2.cvtColor(img_local, cv2.COLOR_BGR2RGB))
        inputs = processor(images=img_pil, return_tensors="pt").to(device, dtype=dtype_ia)

        with torch.no_grad():
            outputs = model(**inputs)
            prof = outputs.predicted_depth

        prof = torch.nn.functional.interpolate(
            prof.unsqueeze(1).float(),
            size=img_local.shape[:2],
            mode="bilinear",
            align_corners=False,
        ).squeeze()

        mapa_np = prof.cpu().numpy()

        p_min, p_max = np.percentile(mapa_np, (2, 98))
        mapa_norm = np.clip((mapa_np - p_min) / (p_max - p_min + 1e-6), 0, 1) * 255.0

        tempo_gasto = time.perf_counter() - t_inicio_ia
        fps_instantaneo = 1.0 / max(tempo_gasto, 1e-6)

        with trava_thread:
            mapa_prof_bruto = mapa_norm
            fps_ia = (0.7 * fps_ia) + (0.3 * fps_instantaneo) if fps_ia > 0 else fps_instantaneo

thread_ia = threading.Thread(target=trabalhador_ia, daemon=True)
thread_ia.start()

# =========================================================================
# 3. INICIALIZA WEBCAM E PAINEL DE CONTROLES
# =========================================================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

janela_ctrl = "Ajustes no Mapa de Profundidade"
cv2.namedWindow(janela_ctrl)
cv2.resizeWindow(janela_ctrl, 480, 250)

# IMPORTANTE: Degrau Relevo em ~28 garante ~6 cores para medir saltos > 1 cor!
cv2.createTrackbar("Degrau Relevo (Z)", janela_ctrl, 28, 80, nada)
cv2.createTrackbar("Sensibilidade Canny", janela_ctrl, 25, 120, nada)
cv2.createTrackbar("Corte Fundo Distante", janela_ctrl, 90, 250, nada)
cv2.createTrackbar("Area Minima", janela_ctrl, 1200, 15000, nada)
cv2.createTrackbar("Suavizacao Temporal", janela_ctrl, 50, 95, nada)

np.random.seed(42)
cores = np.random.randint(50, 255, size=(100, 3), dtype=np.uint8)

mapa_ema = np.zeros((480, 640), dtype=np.float32)
fundo_referencia = None

kernel_limpeza = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
kernel_corte = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# Vizinhança 11x11 para checar se o salto ao redor da borda Canny é maior que 1 cor
kernel_salto = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))

tempo_anterior = time.perf_counter()
fps_video = 0.0

print("Teclas: [b] Capturar mesa vazia | [r] Resetar mesa | [q] Sair")

# =========================================================================
# 4. LOOP PRINCIPAL
# =========================================================================
while True:
    sucesso, frame = cap.read()
    if not sucesso:
        break

    tempo_atual = time.perf_counter()
    dt = tempo_atual - tempo_anterior
    tempo_anterior = tempo_atual
    fps_inst_video = 1.0 / max(dt, 1e-6)
    fps_video = (0.9 * fps_video) + (0.1 * fps_inst_video) if fps_video > 0 else fps_inst_video

    with trava_thread:
        if frame_para_ia is None:
            frame_para_ia = frame
        mapa_recente = mapa_prof_bruto.copy() if mapa_prof_bruto is not None else None
        fps_ia_atual = fps_ia

    if mapa_recente is None:
        cv2.putText(frame, "Iniciando IA...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("3. Mascaras e Bounding Box", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    degrau_z = max(10, cv2.getTrackbarPos("Degrau Relevo (Z)", janela_ctrl))
    limiar_canny = max(5, cv2.getTrackbarPos("Sensibilidade Canny", janela_ctrl))
    corte_fundo = cv2.getTrackbarPos("Corte Fundo Distante", janela_ctrl)
    area_min = cv2.getTrackbarPos("Area Minima", janela_ctrl)
    peso_ema = cv2.getTrackbarPos("Suavizacao Temporal", janela_ctrl) / 100.0

    # 1. Suavização Temporal (EMA)
    mapa_ema = (peso_ema * mapa_ema) + ((1.0 - peso_ema) * mapa_recente)
    mapa_prof_uint8 = mapa_ema.astype(np.uint8)

    if fundo_referencia is not None:
        mapa_trabalho = cv2.subtract(mapa_prof_uint8, fundo_referencia)
        mapa_trabalho = cv2.normalize(mapa_trabalho, None, 0, 255, cv2.NORM_MINMAX)
    else:
        mapa_trabalho = mapa_prof_uint8

    # 2. Filtro Bilateral (Alisa a superfície mantendo bordas reais)
    suave_prof = cv2.bilateralFilter(mapa_trabalho, d=7, sigmaColor=45, sigmaSpace=45)

    # =====================================================================
    # 3. MAPA DE RELEVO (Clusterização por Faixas de Cinza)
    # =====================================================================
    mapa_relevo = np.zeros_like(suave_prof)
    regiao_frente = suave_prof >= corte_fundo

    camadas = (suave_prof[regiao_frente].astype(np.int32) - corte_fundo) // degrau_z
    valores_relevo = np.clip(corte_fundo + (camadas + 1) * degrau_z, 0, 255).astype(np.uint8)
    mapa_relevo[regiao_frente] = valores_relevo

    mapa_relevo = cv2.morphologyEx(mapa_relevo, cv2.MORPH_OPEN, kernel_limpeza, iterations=1)
    mapa_relevo = cv2.morphologyEx(mapa_relevo, cv2.MORPH_CLOSE, kernel_limpeza, iterations=2)

    # =====================================================================
    # 4. SUA IDEIA: CANNY SÓ CORTA ONDE A DIVISÃO FOR > 1 COR DE RELEVO
    # =====================================================================
    # Mede o salto de cor de relevo na vizinhança 11x11
    salto_relevo = cv2.morphologyEx(mapa_relevo, cv2.MORPH_GRADIENT, kernel_salto)
    # Cria uma máscara de permissão: só vale onde a diferença for MAIOR que 1 degrau_z!
    _, zona_salto_maior_que_1 = cv2.threshold(salto_relevo, degrau_z + 2, 255, cv2.THRESH_BINARY)

    # Roda o Canny cirúrgico no mapa contínuo
    bordas_canny = cv2.Canny(suave_prof, limiar_canny, limiar_canny * 2, L2gradient=True)

    # Filtra o Canny: apaga linhas do Canny que estejam em transições suaves (<= 1 cor)
    canny_validado = cv2.bitwise_and(bordas_canny, zona_salto_maior_que_1)

    # Engrossa levemente (3px) e fecha micro-falhas na linha do Canny para isolar objetos
    bordas_totais = cv2.dilate(canny_validado, kernel_corte, iterations=1)
    bordas_totais = cv2.morphologyEx(bordas_totais, cv2.MORPH_CLOSE, kernel_limpeza, iterations=1)

    # Aplica os cortes no Mapa de Relevo e gera a máscara binária
    relevo_cortado = mapa_relevo.copy()
    relevo_cortado[bordas_totais > 0] = 0
    _, mascara_limpa = cv2.threshold(relevo_cortado, 1, 255, cv2.THRESH_BINARY)

    # =====================================================================
    # 5. COMPONENTES CONECTADOS (Resolve o Cubo Mágico) + FILTRO 3D (Resolve a Caneca)
    # =====================================================================
    # Em vez de findContours(RETR_EXTERNAL), connectedComponents acha ilhas mesmo dentro de outros objetos!
    num_labels, matriz_labels, stats, _ = cv2.connectedComponentsWithStats(mascara_limpa, connectivity=8)

    candidatos = []
    # Começa do label 1 (pois o label 0 é sempre o fundo preto / buracos)
    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]
        if area > area_min:
            x = stats[label_id, cv2.CC_STAT_LEFT]
            y = stats[label_id, cv2.CC_STAT_TOP]
            w = stats[label_id, cv2.CC_STAT_WIDTH]
            h = stats[label_id, cv2.CC_STAT_HEIGHT]

            # Calcula a profundidade (relevo) mediana deste objeto específico
            mascara_obj = (matriz_labels == label_id)
            z_medio = float(np.median(suave_prof[mascara_obj]))

            candidatos.append((area, (x, y, w, h), label_id, z_medio))

    # Ordena do MAIOR objeto para o MENOR
    candidatos.sort(key=lambda item: item[0], reverse=True)

    caixas_aprovadas = []
    labels_aprovados = []
    z_aprovados = []

    for area, (x, y, w, h), label_id, z_obj in candidatos:
        dentro_de_outro = False
        for idx_maior, (gx, gy, gw, gh) in enumerate(caixas_aprovadas):
            inter_x1 = max(x, gx)
            inter_y1 = max(y, gy)
            inter_x2 = min(x + w, gx + gw)
            inter_y2 = min(y + h, gy + gh)

            if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                area_inter = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                sobreposicao_2d = area_inter / float(w * h)

                # Diferença de profundidade entre o objeto menor e o objeto maior atrás dele
                diferenca_z = abs(z_obj - z_aprovados[idx_maior])

                # SÓ descarta se estiver dentro da caixa 2D E na MESMA profundidade (< 1.2 degrau)!
                # Se estiver mais perto (como a Caneca ou o Cubo na frente do peito), MANTÉM!
                if sobreposicao_2d > 0.70 and diferenca_z < (degrau_z * 1.2):
                    dentro_de_outro = True
                    break

        if not dentro_de_outro:
            caixas_aprovadas.append((x, y, w, h))
            labels_aprovados.append(label_id)
            z_aprovados.append(z_obj)

    # Pinta cada ilha aprovada diretamente (respeitando buracos e objetos sobrepostos!)
    mascaras_coloridas = np.zeros_like(frame)
    for indice_obj, label_id in enumerate(labels_aprovados):
        cor = cores[indice_obj % 100]
        mascaras_coloridas[matriz_labels == label_id] = cor

    sobreposicao = cv2.addWeighted(frame, 0.65, mascaras_coloridas, 0.35, 0)

    for (x, y, w, h) in caixas_aprovadas:
        cv2.rectangle(sobreposicao, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Painel de FPSe
    cv2.rectangle(sobreposicao, (10, 10), (260, 70), (0, 0, 0), cv2.FILLED)
    cv2.putText(sobreposicao, f"FPS Video: {fps_video:.1f}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    cv2.putText(sobreposicao, f"FPS IA (3D): {fps_ia_atual:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    mapa_prof_cor = cv2.applyColorMap(suave_prof, cv2.COLORMAP_INFERNO)

    cv2.imshow("1. Mapa de Profundidade", mapa_prof_cor)
    cv2.imshow("2. Mapa de Relevo + Canny (>1 Cor)", relevo_cortado)
    cv2.imshow("3. Mascaras e Bounding Box", sobreposicao)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord("q"):
        rodando = False
        break
    elif tecla == ord("b"):
        fundo_referencia = mapa_prof_uint8.copy()
        print("Fundo da mesa capturado!")
    elif tecla == ord("r"):
        fundo_referencia = None
        print("Fundo resetado!")

cap.release()
cv2.destroyAllWindows()