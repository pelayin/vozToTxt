import pyautogui
import os
import tempfile
import wave
import pyaudio
import keyboard
import pyperclip
from groq import Groq  # https://console.groq.com/keys <txtToVoz>

client = Groq(api_key="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")


def grabar_audio(frecuencia_muestreo=16000, canales=1, fragmento=1024):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=canales,
        rate=frecuencia_muestreo,
        input=True,
        frames_per_buffer=fragmento,
    )
    print("Presiona y mantén pulsado el botón <INS> para comenzar a grabar...")
    frames = []
    keyboard.wait("insert")
    print("Grabando...(Suelta <INS> para detener...)")
    while keyboard.is_pressed("insert"):
        data = stream.read(fragmento)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    return frames, frecuencia_muestreo


def guardar_audio(frames, frecuencia_muestreo):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp:
        wf = wave.open(audio_temp.name, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(frecuencia_muestreo)
        wf.writeframes(b"".join(frames))
        wf.close()
        return audio_temp.name


def transcribir_audio(ruta_archivo_audio):
    try:
        with open(ruta_archivo_audio, "rb") as archivo:
            transcripcion = client.audio.transcriptions.create(
                file=(os.path.basename(ruta_archivo_audio), archivo.read()),
                model="whisper-large-v3",
                prompt="el audio es de una persona normal, trabajando",
                response_format="text",
                language="es",
            )
        return transcripcion
    except Exception as e:
        print(f"Error al transcribir el audio: {str(e)}")
        return None


# def copiar_transcripcion_al_portapapeles(transcripcion):
#     pyperclip.copy(transcripcion)
#     pyperclip.paste()  # esto es mio por la línea de abajo, parece igual
#     # pyautogui.hotkey("ctrl", "v")


def main():
    while True:
        frames, frecuencia_muestreo = grabar_audio()
        archivo_audio_temp = guardar_audio(frames, frecuencia_muestreo)
        print("Transcribiendo...")
        transcripcion = transcribir_audio(archivo_audio_temp)
        if transcripcion:
            print(
                "----- Copiando... --------------------------------------------------------"
            )
            pyperclip.copy(transcripcion)
            print("\n" + transcripcion + "\n")
            pyautogui.hotkey("ctrl", "v")
            # pyperclip.paste()  # esto es mio por la línea de abajo
            print(
                "----- Transcripción copiada al portapapeles y pegada a la aplicación -----"
            )
        else:
            print("Error al transcribir el audio")

        os.unlink(archivo_audio_temp)
        print("\nListo para la próxima grabación...")


if __name__ == "__main__":
    main()
