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

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="Traductor por Voz")


# --- 2. TÍTULO Y DESCRIPCIÓN ---
st.title("🎙️ Traductor de Voz Interactivo")
st.markdown("¡Hola! Basado en tu interés en el **diseño de interacción (UX)**, he rediseñado esta app para que sea más organizada y fácil de usar, manteniendo la misma funcionalidad que te gusta.")
st.write("Presiona el botón para hablar, y luego elige los idiomas para escuchar la traducción.")

image = Image.open('talking.jpg')
# Centramos la imagen y el botón para un mejor enfoque visual
_, col_img, _ = st.columns([1, 2, 1])
with col_img:
    st.image(image, width=350)
    st.write("") # Espacio
    # Botón principal para iniciar la escucha
    stt_button = Button(label=" ¡Presiona para Hablar! 🎤", button_type="primary", width=300, height=50)


# --- 3. LÓGICA DE CAPTURA DE VOZ (SIN CAMBIOS) ---
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

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)


# --- 4. PROCESAMIENTO Y RESULTADOS ---
if result:
    if "GET_TEXT" in result:
        text = str(result.get("GET_TEXT"))
        
        st.divider()
        st.subheader("Texto Detectado:")
        st.info(f'🗣️ "{text}"') # Usamos st.info para resaltar el texto
        st.divider()

        try:
            os.mkdir("temp")
        except:
            pass

        translator = Translator()
        
        # --- Configuración de Idiomas en Columnas
