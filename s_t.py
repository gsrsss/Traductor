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

# --- DEFINICIÓN DE IDIOMAS (15 más hablados con Coreano) ---
IDIOMAS_DISPONIBLES = {
    "Inglés": "en",
    "Chino Mandarín": "zh-cn", 
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
    "Maratí": "mr",
    "Coreano": "ko" 
}
# Lista de nombres de idiomas para el SelectBox
NOMBRES_IDIOMAS = list(IDIOMAS_DISPONIBLES.keys())

# --- CONFIGURACIÓN DE STREAMLIT ---
st.title("TRADUCTOR")
st.subheader("¡Comunícate con todos!")
st.write("No entiendes lo que dice alguien? No te preocupes! Yo escucho lo que están diciendo, y lo traduzco!")

image = Image.open('talking.jpg')

st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    # Lista de idiomas en el sidebar
    st.markdown("### Idiomas disponibles:")
    for nombre in NOMBRES_IDIOMAS:
        st.write(f"- {nombre}")

    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona"  
             " la configuración de lenguaje que necesites.")

st.write("Toca el botón y habla lo que quires traducir")

# --- FUNCIONALIDAD DE VOZ A TEXTO (NO SE MODIFICÓ) ---
stt_button = Button(label=" Escuchar  🎤", width=300,  height=50)

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

# --- PROCESAMIENTO DE TRADUCCIÓN (Activado si hay un resultado de voz) ---
if result and "GET_TEXT" in result:
    
    recognized_text = result.get("GET_TEXT")
    st.markdown("## Texto Reconocido:")
    st.write(recognized_text)

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass
        
    st.markdown("---")
    st.title("Traducción y Audio")
    translator = Translator()
    
    # 1. Selección de Idioma de Entrada
    in_lang_name = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        NOMBRES_IDIOMAS,
        key="select_in_lang" 
    )
    input_language = IDIOMAS_DISPONIBLES[in_lang_name]
    
    # 2. Selección de Idioma de Salida
    out_lang_name = st.selectbox(
        "Selecciona el lenguaje de salida",
        NOMBRES_IDIOMAS,
        key="select_out_lang" 
    )
    output_language = IDIOMAS_DISPONIBLES
