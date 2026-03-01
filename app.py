"""
TRADUCTOR DE LENGUAJE DE SEÑAS - VERSIÓN WEB (STREAMLIT)
--------------------------------------------------------
Este script está adaptado para ejecutarse en navegadores web a través
de Streamlit Cloud usando WebRTC para capturar la cámara del usuario.
"""

import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Configuración de la página
st.set_page_config(page_title="Traductor de Señas AI", layout="wide")
st.title("🤟 Traductor de Lenguaje de Señas en Vivo")
st.write("Permite el acceso a tu cámara para comenzar la traducción en tiempo real.")

# Inicialización de MediaPipe
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Lógica de Reconocimiento de Gestos
def reconocer_gesto_estatico(hand_landmarks, label):
    puntas = [4, 8, 12, 16, 20] 
    dedos_levantados = []

    if label == "Right":
        if hand_landmarks.landmark[puntas[0]].x < hand_landmarks.landmark[puntas[0] - 1].x:
            dedos_levantados.append(1)
        else:
            dedos_levantados.append(0)
    else: 
        if hand_landmarks.landmark[puntas[0]].x > hand_landmarks.landmark[puntas[0] - 1].x:
            dedos_levantados.append(1)
        else:
            dedos_levantados.append(0)

    for id in range(1, 5):
        if hand_landmarks.landmark[puntas[id]].y < hand_landmarks.landmark[puntas[id] - 2].y:
            dedos_levantados.append(1)
        else:
            dedos_levantados.append(0)

    # Diccionario
    if dedos_levantados == [0, 0, 0, 0, 0]: return "Puno / Letra A"
    elif dedos_levantados == [1, 1, 1, 1, 1]: return "Palma / Hola"
    elif dedos_levantados == [0, 1, 1, 0, 0]: return "Paz / Letra V"
    elif dedos_levantados == [1, 1, 0, 0, 1]: return "Te Amo (ASL)"
    elif dedos_levantados == [1, 0, 0, 0, 0]: return "Bien / Pulgar Arriba"
    elif dedos_levantados == [0, 1, 0, 0, 0]: return "Letra D / Apuntar"
    elif dedos_levantados == [0, 0, 0, 0, 1]: return "Letra I"
    
    return "Desconocido"

# Clase que procesa el video frame a frame para WebRTC
class ProcesadorVideo:
    def __init__(self):
        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        # Convertir el frame de WebRTC a un formato que OpenCV entienda
        img = frame.to_ndarray(format="bgr24")
        
        # Procesamiento MediaPipe
        img.flags.writeable = False
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resultados = self.holistic.process(img_rgb)
        img.flags.writeable = True

        gesto_actual = "Esperando gesto..."

        # Dibujar Pose
        if resultados.pose_landmarks:
            mp_drawing.draw_landmarks(img, resultados.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

        # Procesar Manos
        if resultados.left_hand_landmarks:
            mp_drawing.draw_landmarks(img, resultados.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            gesto = reconocer_gesto_estatico(resultados.left_hand_landmarks, "Left")
            if gesto != "Desconocido": gesto_actual = gesto

        if resultados.right_hand_landmarks:
            mp_drawing.draw_landmarks(img, resultados.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            gesto = reconocer_gesto_estatico(resultados.right_hand_landmarks, "Right")
            if gesto != "Desconocido": gesto_actual = gesto

        # Dibujar Interfaz en el video
        cv2.rectangle(img, (0,0), (640, 60), (0, 0, 0), -1)
        cv2.putText(img, f'Traduccion: {gesto_actual}', (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Devolver el frame modificado
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Configuración de los servidores STUN/TURN (Necesario para que el video funcione en la nube)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Componente principal de Streamlit WebRTC
st.write("### Cámara")
webrtc_streamer(
    key="traductor-senas",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=ProcesadorVideo,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)

st.markdown("---")
st.markdown("**Nota Técnica:** Esta versión utiliza `streamlit-webrtc` para procesar el video de forma segura directamente desde tu navegador hacia el servidor de Streamlit.")
