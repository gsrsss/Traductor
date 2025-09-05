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

# --- Configuración de la Página y Estilos ---
st.set_page_config(layout="centered", page_title="Traductor Multimodal")

st.title("TRADUCTOR MULTIMODAL 翻译者")
st.write("Traduce usando tu voz o texto. ¡La comunicación sin fronteras es posible!")

# --- DICCIONARIOS PARA SIMPLIFICAR EL CÓDIGO ---
# Diccionario de idiomas para evitar largos bloques if/elif
LANGUAGES = {
    "Español": "es",
    "Inglés": "en",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
    "Coreano": "ko",
    "Bengalí": "bn",
}

# Diccionario de acentos para gTTS
ACCENTS = {
    "Defecto": "com",
    "Español (México)": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}

# --- WIDGETS COMPARTIDOS (SELECCIÓN DE IDIOMA Y ACENTO) ---
# Se colocan fuera de las pestañas para que la configuración se aplique a ambas
st.header("1. Configura los Idiomas")
col1, col2 = st.columns(2)
with col1:
    in_lang_name = st.selectbox("Idioma de Origen:", list(LANGUAGES.keys()))
    input_language = LANGUAGES[in_lang_name]
with col2:
    out_lang_name = st.selectbox("Idioma de Destino:", list(LANGUAGES.keys()))
    output_language = LANGUAGES[out_lang_name]

english_accent_name = st.selectbox("Selecciona el acento para el audio:", list(ACCENTS.keys()))
tld = ACCENTS[english_accent_name]

# --- Inicialización del Traductor ---
translator = Translator()

# --- Funciones Auxiliares ---
# Se mantiene la función original, es reutilizable
def text_to_speech(input_lang, output_lang, text, accent_tld):
    try:
        translation = translator.translate(text, src=input_lang, dest=output_lang)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_lang, tld=accent_tld, slow=False)
        
        # Crea un nombre de archivo seguro
        my_file_name = text.strip().replace(" ", "_")[0:20] if text else "audio"
        
        # Crea el directorio si no existe
        os.makedirs("temp", exist_ok=True)
        
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None, None

def remove_files(n):
    """Elimina archivos mp3 más antiguos que n días."""
    if not os.path.exists("temp"):
        return
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            os.remove(f)
            print(f"Eliminado archivo antiguo: {f}")

# --- INTERFAZ CON PESTAÑAS ---
st.header("2. Elige tu Método de Traducción")
tab_voice, tab_text = st.tabs(["Traducción por Voz 🎤", "Traducción por Texto 📝"])


# --- Pestaña 1: Traducción por Voz ---
with tab_voice:
    st.write("Presiona el botón y di la frase que quieres traducir.")
    
    stt_button = Button(label=" Empezar a escuchar 🎤", width=300, height=50, button_type="primary")
    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false; // Cambiado a false para capturar una sola frase
        recognition.interimResults = true;

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value !== "") {
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
        debounce_time=0
    )

    if result and "GET_TEXT" in result:
        text_from_speech = result.get("GET_TEXT")
        st.info(f"Texto reconocido: \"{text_from_speech}\"")
        
        st.subheader("Resultado de la Traducción")
        filename, translated_text = text_to_speech(input_language, output_language, text_from_speech, tld)
        
        if filename and translated_text:
            st.write(f"**Texto traducido:** {translated_text}")
            try:
                audio_file = open(f"temp/{filename}.mp3", "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
            except FileNotFoundError:
                st.error("No se pudo generar el archivo de audio. Inténtalo de nuevo.")

# --- Pestaña 2: Traducción por Texto (NUEVA FUNCIONALIDAD) ---
with tab_text:
    st.write("Escribe o pega el texto que deseas traducir en el siguiente campo.")
    
    text_to_translate = st.text_area("Texto a traducir:", height=150)
    
    if st.button("Traducir Texto 📝", use_container_width=True):
        if text_to_translate:
            st.subheader("Resultado de la Traducción")
            
            # Reutilizamos la misma función de texto a audio
            filename, translated_text = text_to_speech(input_language, output_language, text_to_translate, tld)
            
            if filename and translated_text:
                st.write(f"**Texto traducido:**")
                st.success(f"{translated_text}")

                # Opción para mostrar el audio
                st.write("**Audio del texto traducido:**")
                try:
                    audio_file = open(f"temp/{filename}.mp3", "rb")
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)
                except FileNotFoundError:
                    st.error("No se pudo generar el archivo de audio. Inténtalo de nuevo.")
        else:
            st.warning("Por favor, ingresa un texto para traducir.")

# --- Limpieza de archivos viejos al final del script ---
remove_files(1) # Limpia archivos de más de 1 día
