import os
import time
import glob
from PIL import Image

import streamlit as st

# Importaciones para el botón de escucha y eventos
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Importaciones para traducción y Texto a Voz
from gtts import gTTS
from googletrans import Translator

# --- Configuración Inicial y Títulos ---
st.set_page_config(page_title="Traductor de Voz y Texto")

st.title("TRADUCTOR 🗣️")
st.subheader("¡Comunícate con todos!")
st.write(
    "¿No entiendes lo que dice alguien? ¡No te preocupes! Yo escucho lo que están diciendo, y lo traduzco."
)

# Cargar y mostrar la imagen
try:
    image = Image.open('talking.jpg')
    st.image(image, width=300)
except FileNotFoundError:
    st.warning("Asegúrate de que el archivo 'talking.jpg' esté en el mismo directorio.")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.subheader("Instrucciones del Traductor.")
    st.write(
        "Presiona el botón. Cuando escuches la señal 🔔, "
        "habla lo que quieres traducir. Luego selecciona "
        "la configuración de lenguaje que necesites."
    )

# --- Botón de Escucha (Speech-to-Text) ---
st.write("Toca el botón y habla lo que quieres traducir:")

stt_button = Button(label=" Escuchar 🎤", width=300, height=50)

# Código JavaScript para el reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Captura el resultado del evento de Bokeh
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# --- Lógica de Traducción
