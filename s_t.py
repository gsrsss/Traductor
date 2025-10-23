import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob

from gtts import gTTS
from googletrans import Translator

# --- Configuración de Idiomas ---
# Los 15 idiomas más hablados (aproximado, basado en total de hablantes)
IDIOMAS_DISPONIBLES = {
    "Inglés": "en",
    "Mandarín (Chino)": "zh-cn", # Código para gTTS
    "Hindi": "hi",
    "Español": "es",
    "Francés": "fr",
    "Árabe": "ar",
    "Bengalí": "bn",
    "Portugués": "pt",
    "Ruso": "ru",
    "Urdu": "ur",
    "Indonesio": "id",
    "Alemán": "de",
    "Japonés": "ja",
    "Coreano": "ko",
    "Turco": "tr", # Agregando un 15º idioma común
}

# Diccionario para el mapeo de acentos en inglés (tld para gTTS)
ACENTOS_INGLES = {
    "Defecto": "com",
    "Español (México)": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}

# --- Interfaz de Streamlit ---
st.title("TRADUCTOR 🗣️")
st.subheader("¡Comunícate con todos! 🌐")
st.write("¿No entiendes lo que dice alguien? ¡No te preocupes! Yo escucho lo que están diciendo, y lo traduzco.")

try:
    # Asegúrate de que tienes una imagen llamada 'talking.jpg' en el mismo directorio.
    image = Image.open('talking.jpg')
    st.image(image, width=300)
except FileNotFoundError:
    st.warning("Aviso: No se encontró la imagen 'talking.jpg'. Usará el espacio vacío.")

with st.sidebar:
    st.subheader("Traductor. 💬")
    st.write(
        "Presiona el botón, cuando escuches la señal "
        "habla lo que quieres traducir, luego selecciona"
        " la configuración de lenguaje que necesites."
    )

st.write("Toca el botón y habla lo que quieres traducir")

# --- Componente de Reconocimiento de Voz (STT) ---
stt_button = Button(label=" Escuchar 🎤", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkit
        # 2. Conversión a Voz (Text-to-Speech)
        try:
            # gTTS usa el código de idioma, y 'tld' solo es relevante para inglés.
            tts = gTTS
