import os
import tempfile
import time
import logging
import subprocess
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import whisper
import torch
from PIL import Image
from transformers import pipeline
from diffusers import StableDiffusionPipeline

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

GENERATED_FOLDER = 'generated'
os.makedirs(GENERATED_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        app.logger.info("🎬 FFmpeg detected.")
    except Exception:
        app.logger.warning("⚠️ FFmpeg not installed. Whisper may not handle MP3 properly.")

whisper_model = None
translator = None
diffusion_pipe = None

def load_models():
    global whisper_model, translator, diffusion_pipe

    # Whisper
    app.logger.info("🔊 Loading Whisper (base)...")
    whisper_model = whisper.load_model("base")
    app.logger.info("✅ Whisper ready.")

    # Translation Pipeline
    app.logger.info("🌍 Loading translation model...")
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
    app.logger.info("✅ Translator ready.")

    # GPU / CPU Mode
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    app.logger.info(f"🖥 Using device: {device} | dtype: {dtype}")

    # Stable Diffusion — SD v1.5 (Faster for CPU)
    app.logger.info("🎨 Loading Stable Diffusion (SD v1.5)...")
    diffusion_pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
        safety_checker=None   # SPEED BOOST
    ).to(device)

    app.logger.info("✅ Stable Diffusion ready!")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/generated/<path:filename>')
def generated_file(filename):
    return send_from_directory(GENERATED_FOLDER, filename)

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio_endpoint():
    global whisper_model, translator

    if 'audioFile' not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    audio_file = request.files['audioFile']
    language = request.form.get("language", "english").strip()

    tmp_file_path = None

    try:
        # Save temp audio file
        ext = os.path.splitext(audio_file.filename)[1] or ".wav"
        tmp_dir = tempfile.gettempdir()
        tmp_file_path = os.path.join(tmp_dir, f"audio_{int(time.time())}{ext}")
        audio_file.save(tmp_file_path)

        if not os.path.exists(tmp_file_path):
            raise FileNotFoundError("Uploaded file missing after save.")

        # Whisper Transcription (FP32 on CPU)
        app.logger.info("🗣 Running Whisper transcription...")
        result = whisper_model.transcribe(tmp_file_path, fp16=False, language=None)
        transcribed_text = result.get("text", "").strip()

        if not transcribed_text:
            return jsonify({"error": "Whisper could not detect speech"}), 500

        # Translation (if needed)
        prompt = transcribed_text
        if language == "other":
            app.logger.info("🌍 Translating text to English...")
            prompt = translator(transcribed_text)[0]["translation_text"].strip()

        return jsonify({
            "transcribed_text": transcribed_text,
            "prompt": prompt
        })

    except Exception as e:
        app.logger.error(f"❌ Transcription error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            app.logger.info("🧹 Temp audio deleted.")

@app.route('/generate-image', methods=['POST'])
def generate_image_endpoint():
    global diffusion_pipe, translator

    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        language = data.get("language", "english").strip()

        if not prompt:
            return jsonify({"error": "Prompt is empty"}), 400

        # Translate if needed
        if language == "other":
            app.logger.info("🌍 Translating prompt...")
            prompt = translator(prompt)[0]["translation_text"].strip()

        # Generate image
        app.logger.info(f"🎨 Generating image for: {prompt}")
        image = diffusion_pipe(prompt, num_inference_steps=30).images[0]
        image = image.resize((512, 400))

        # Save
        filename = f"img_{int(time.time())}.png"
        save_path = os.path.join(GENERATED_FOLDER, filename)
        image.save(save_path)

        image_url = f"{request.host_url.rstrip('/')}/generated/{filename}"

        return jsonify({"image_url": image_url})

    except Exception as e:
        app.logger.error(f"❌ Image generation error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.logger.info("🚀 Checking environment...")
    check_ffmpeg()

    app.logger.info("🚀 Loading models (this takes time only once)...")
    load_models()

    app.logger.info("✅ Server is ready at http://127.0.0.1:5000/")
    app.run(debug=True, host="127.0.0.1", port=5000)

