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
NOMBRES_IDIOMAS = list(IDIOMAS_DISPONIBLES.keys())

# --- CONFIGURACIÓN DE STREAMLIT ---
st.title("TRADUCTOR")
st.subheader("¡Comunícate con todos! 🗣️")
st.write("Yo escucho lo que dicen, y lo traduzco. ¡Presiona 'Escuchar' para empezar!")

image = Image.open('talking.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    st.markdown("### Idiomas disponibles:")
    for nombre in NOMBRES_IDIOMAS:
        st.write(f"- {nombre}")
    st.write("Presiona el botón, habla lo que quieres traducir, luego selecciona la configuración de lenguaje.")

st.write("Toca el botón y habla lo que quieres traducir 👇")

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
    stt_button, events="GET_TEXT", key="listen", refresh_on_update=False, 
    override_height=75, debounce_time=0
)

# --- PROCESAMIENTO DE TRADUCCIÓN ---
if result and "GET_TEXT" in result:
    
    recognized_text = result.get("GET_TEXT")
    st.markdown("## Texto Reconocido:")
    st.info(recognized_text)

    # Configuración de archivos temporales
    try:
        os.mkdir("temp")
    except FileExistsError:
        pass
        
    st.markdown("---")
    st.title("Configuración de Traducción")
    translator = Translator()
    
    # 1. Selección de Idioma de Entrada
    in_lang_name = st.selectbox(
        "Selecciona el lenguaje de Entrada", NOMBRES_IDIOMAS, key="select_in_lang" 
    )
    input_language = IDIOMAS_DISPONIBLES[in_lang_name]
    
    # 2. Selección de Idioma de Salida
    out_lang_name = st.selectbox(
        "Selecciona el lenguaje de salida", NOMBRES_IDIOMAS, key="select_out_lang" 
    )
    output_language = IDIOMAS_DISPONIBLES[out_lang_name]

    # --- LÓGICA DE ACENTO ---
    english_accent = st.selectbox(
        "Selecciona el acento (Aplica mejor a Inglés/Español)",
        ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"),
    )
    
    tld_map = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", 
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au", 
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    tld = tld_map.get(english_accent, "com")
    
    
    def text_to_speech(input_lang, output_lang, text_to_translate, accent_tld):
        """Traduce el texto y lo convierte a audio."""
        trans_text = "Traducción fallida."
        file_name = None
        try:
            translation = translator.translate(text_to_translate, src=input_lang, dest=output_lang)
            trans_text = translation.text
            
            tts = gTTS(trans_text, lang=output_lang, tld=accent_tld, slow=False) 
            
            safe_name = text_to_translate[:20].replace(" ", "_").replace("/", "") or "audio"
            file_name = safe_name
            file_path = f"temp/{file_name}.mp3"
            tts.save(file_path)
            
            return file_name, trans_text
        except Exception as e:
            st.error(f"Error al traducir o generar audio. Intenta con un texto más corto o cambia los idiomas. Detalle: {e}")
            return None, trans_text # Devuelve el texto de error si falla
    
    
    display_output_text = st.checkbox("Mostrar el texto de la traducción")
    
    # --- EJECUCIÓN AL PULSAR EL BOTÓN ---
    if st.button("Convertir y Traducir"): 
        
        file_name, output_text = text_to_speech(input_language, output_language, recognized_text, tld)
        
        if file_name:
            # 3. Se escribe la traducción y se reproduce el audio
            st.markdown(f"## ✅ Traducción Completa")
            
            if display_output_text:
                st.markdown(f"**Texto Traducido a {out_lang_name}:**")
                st.success(f" {output_text}") # Usamos st.success para resaltarlo
            
            audio_file_path = f"temp/{file_name}.mp3"
            
            try:
                with open(audio_file_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.markdown(f"**Audio de la Traducción:**")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
            except FileNotFoundError:
                st.error("Error: Archivo de audio temporal no encontrado.")
        
    
    # Función para limpiar archivos temporales
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days: 
                    try:
                        os.remove(f)
                    except OSError:
                        pass # Ignora errores de borrado de archivos en uso

    remove_files(7)
