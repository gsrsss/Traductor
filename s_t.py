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

# --- NUEVA DEFINICIÓN DE IDIOMAS (15 más hablados con Coreano) ---
IDIOMAS_DISPONIBLES = {
    "Inglés": "en",
    "Chino Mandarín": "zh-cn", # Código común para Mandarín/Chino simplificado
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
    "Coreano": "ko" # Reemplaza a Telugu
}
# Lista de nombres de idiomas para el SelectBox
NOMBRES_IDIOMAS = list(IDIOMAS_DISPONIBLES.keys())

# --- RESTO DEL CÓDIGO BASE ---
st.title("TRADUCTOR")
st.subheader("¡Comunícate con todos!")
st.write("No entiendes lo que dice alguien? No te preocupes! Yo escucho lo que están diciendo, y lo traduzco!")

image = Image.open('talking.jpg')

st.image(image,width=300)

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

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass
    st.title("Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    
    # --- LÓGICA DE SELECCIÓN DE IDIOMAS MEJORADA ---
    in_lang_name = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        NOMBRES_IDIOMAS,
    )
    # Asigna el código usando el diccionario
    input_language = IDIOMAS_DISPONIBLES[in_lang_name]
    
    out_lang_name = st.selectbox(
        "Selecciona el lenguaje de salida",
        NOMBRES_IDIOMAS,
    )
    # Asigna el código usando el diccionario
    output_language = IDIOMAS_DISPONIBLES[out_lang_name]

    # --- LÓGICA DE SELECCIÓN DE ACENTO (sin cambios) ---
    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )
    
    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "Español":
        tld = "com.mx"
    
    elif english_accent == "Reino Unido":
        tld = "co.uk"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Irlanda":
        tld = "ie"
    elif english_accent == "Sudáfrica":
        tld = "co.za"
    
    
    def text_to_speech(input_language, output_language, text, tld):
        # Esta función usa la funcionalidad base de gTTS y googletrans
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        # NOTA: gTTS (usado en tu código) soporta la mayoría de estos idiomas
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False) 
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    
    display_output_text = st.checkbox("Mostrar el texto")
    
    if st.button("convert
