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
        key="select_in_lang" # Agregado key para evitar errores si el usuario interactúa
    )
    input_language = IDIOMAS_DISPONIBLES[in_lang_name]
    
    # 2. Selección de Idioma de Salida
    out_lang_name = st.selectbox(
        "Selecciona el lenguaje de salida",
        NOMBRES_IDIOMAS,
        key="select_out_lang" # Agregado key para evitar errores si el usuario interactúa
    )
    output_language = IDIOMAS_DISPONIBLES[out_lang_name]

    # --- LÓGICA DE SELECCIÓN DE ACENTO (sin cambios) ---
    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto", "Español", "Reino Unido", "Estados Unidos",
            "Canada", "Australia", "Irlanda", "Sudáfrica",
        ),
    )
    
    tld_map = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", 
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au", 
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    tld = tld_map.get(english_accent, "com")
    
    
    def text_to_speech(input_lang, output_lang, text_to_translate, accent_tld):
        """Traduce el texto y lo convierte a audio."""
        try:
            translation = translator.translate(text_to_translate, src=input_lang, dest=output_lang)
            trans_text = translation.text
            # gTTS es sensible al idioma de salida, usa el tld si aplica, o 'com' por defecto.
            tts = gTTS(trans_text, lang=output_lang, tld=accent_tld, slow=False) 
            
            # Crea un nombre de archivo seguro
            my_file_name = text_to_translate[:20].replace(" ", "_").replace("/", "") or "audio"
            file_path = f"temp/{my_file_name}.mp3"
            tts.save(file_path)
            return my_file_name, trans_text
        except Exception as e:
            st.error(f"Error durante la traducción/audio: {e}")
            return None, "Error de traducción."

    
    display_output_text = st.checkbox("Mostrar el texto de la traducción")
    
    # --- EL BOTÓN CLAVE QUE EJECUTA LA TRADUCCIÓN ---
    # Al pulsarse, se inicia el proceso de traducción y generación de audio.
    if st.button("Convertir y Traducir"):
