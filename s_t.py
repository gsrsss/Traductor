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
# 'Nombre en español': ('Código para googletrans/gTTS', 'Dominio tld para acento por defecto (si aplica para gTTS en inglés)')
IDIOMAS_DISPONIBLES = {
    "Inglés": "en",
    "Mandarín (Chino)": "zh-cn",
    "Hindi": "hi",
    "Español": "es",
    "Francés": "fr",
    "Árabe": "ar",
    "Bengalí": "bn",
    "Portugués": "pt",
    "Ruso": "ru",
    "Urdu": "ur", # Nota: El código 'ur' se usa para gTTS
    "Indonesio": "id",
    "Alemán": "de",
    "Japonés": "ja",
    "Maratí": "mr",
    "Telugú": "te",
    "Coreano": "ko",
    # Agregué Coreano de la lista original por si se prefiere sobre Maratí o Telugú,
    # y ya estaba implementado en tu código. Maratí/Telugú son menos comunes en gTTS.
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
    image = Image.open('talking.jpg')
    st.image(image, width=300)
except FileNotFoundError:
    st.warning("Aviso: No se encontró la imagen 'talking.jpg'.")


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
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false; // Cambiado a false para una sola frase
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
            recognition.stop(); // Detener después de obtener el resultado final
        }
    }
    
    recognition.onerror = function(e) {
        console.error(e);
        recognition.stop();
    }
    
    recognition.start();
    console.log("Reconocimiento iniciado...");
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# --- Proceso de Traducción y TTS ---
if result:
    if "GET_TEXT" in result:
        st.markdown(f"**Tu voz (transcrito):** *{result.get('GET_TEXT')}*")

    try:
        os.makedirs("temp", exist_ok=True)
    except:
        pass # La carpeta ya existe o no se pudo crear.

    st.title("Texto a Audio y Traducción")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    
    # Selectores de Idioma
    idioma_nombres = list(IDIOMAS_DISPONIBLES.keys())

    # Establecer la selección por defecto en un idioma común si es posible
    default_in_index = idioma_nombres.index("Español") if "Español" in idioma_nombres else 0
    default_out_index = idioma_nombres.index("Inglés") if "Inglés" in idioma_nombres else 0

    in_lang_name = st.selectbox(
        "Selecciona el **lenguaje de Entrada** (el idioma en el que hablaste):",
        idioma_nombres,
        index=default_in_index
    )
    
    out_lang_name = st.selectbox(
        "Selecciona el **lenguaje de Salida** (el idioma al que quieres traducir):",
        idioma_nombres,
        index=default_out_index
    )

    input_language = IDIOMAS_DISPONIBLES[in_lang_name]
    output_language = IDIOMAS_DISPONIBLES[out_lang_name]
    
    # Selector de Acento (solo relevante si la salida es Inglés)
    tld = ACENTOS_INGLES["Defecto"] # Valor por defecto
    if out_lang_name == "Inglés":
        english_accent = st.selectbox(
            "Selecciona el **acento** (solo para inglés de salida):",
            list(ACENTOS_INGLES.keys()),
        )
        tld = ACENTOS_INGLES[english_accent]
    
    
    # Función de Traducción y Síntesis de Voz
    @st.cache_data(show_spinner=False)
    def text_to_speech(input_lang_code, output_lang_code, text_to_translate, tld_accent):
        """Traduce el texto y lo convierte a voz."""
        
        # 1. Traducción
        translation = translator.translate(text_to_translate, src=input_lang_code, dest=output_lang_code)
        trans_text = translation.text
        
        # 2. Conversión a Voz (Text-to-Speech)
        try:
            # gTTS usa el código de idioma, y 'tld' solo es relevante para inglés.
            tts = gTTS
