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

# --- CÓDIGO ORIGINAL SIN CAMBIOS ---
st.title("TRADUCTOR")
st.subheader("¡Comunícate con todos!")
st.write("No entiendes lo que dice alguien? No te preocupes! Yo escucho lo que están diciendo, y lo traduzco!")

image = Image.open('talking.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona"
             " la configuración de lenguaje que necesites.")

# --- INICIO DE LA NUEVA SECCIÓN: TRADUCCIÓN POR TEXTO ---
st.subheader("Opción 1: Traducir Texto Escrito 📝")

# Usamos una clave única para el área de texto para evitar conflictos
text_input = st.text_area("Escribe aquí el texto que quieres traducir:", key="text_input_area")

# Se crea una instancia del traductor para esta sección
translator_text = Translator()

# Se copian los selectores de idioma para que esta sección sea independiente
in_lang_text = st.selectbox(
    "Selecciona el lenguaje de Entrada",
    ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    key="in_lang_text"
)
out_lang_text = st.selectbox(
    "Selecciona el lenguaje de salida",
    ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    key="out_lang_text"
)
english_accent_text = st.selectbox(
    "Selecciona el acento",
    ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"),
    key="accent_text"
)

# Lógica para la traducción de texto al presionar un botón
if st.button("Traducir Texto", key="translate_text_button"):
    if text_input:
        # Asignación de códigos de idioma
        lang_map = {"Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"}
        input_language_text = lang_map[in_lang_text]
        output_language_text = lang_map[out_lang_text]

        # Asignación de acentos
        accent_map = {"Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au", "Irlanda": "ie", "Sudáfrica": "co.za"}
        tld_text = accent_map[english_accent_text]

        # Proceso de traducción y conversión a audio
        translation = translator_text.translate(text_input, src=input_language_text, dest=output_language_text)
        trans_text = translation.text
        
        tts = gTTS(trans_text, lang=output_language_text, tld=tld_text, slow=False)
        
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass
            
        file_name = text_input[0:20].replace(" ", "_") if text_input else "audio_text"
        tts.save(f"temp/{file_name}.mp3")
        
        # Mostrar resultados
        st.markdown("## Texto de salida:")
        st.write(f" {trans_text}")
        
        audio_file = open(f"temp/{file_name}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    else:
        st.warning("Por favor, ingresa un texto para traducir.")

# Divisor para separar las dos funcionalidades
st.divider()

# --- FIN DE LA NUEVA SECCIÓN ---


# --- INICIO DEL CÓDIGO ORIGINAL PARA TRADUCCIÓN POR VOZ ---
st.subheader("Opción 2: Traducir con tu Voz 🎤")
st.write("Toca el botón y habla lo que quieres traducir")

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
        st.write("Texto reconocido: ", result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass
    st.title("Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"), key="in_lang_voice"
    )
    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "Coreano":
        input_language = "ko"
    elif in_lang == "Mandarín":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"
    
    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"), key="out_lang_voice"
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "Coreano":
        output_language = "ko"
    elif out_lang == "Mandarín":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"
    
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
        ), key="accent_voice"
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
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    
    display_output_text = st.checkbox("Mostrar el texto")
    
    if st.button("convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f" {output_text}")
    
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
