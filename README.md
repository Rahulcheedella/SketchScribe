# 🎨 Speech-to-Sketch (Local AI Web Application)
Convert speech into sketches using local Whisper + Stable Diffusion.  
This project runs **fully offline** except for initial package download.  

---

## 📌 Overview

This project allows a user to:

1. Upload an audio file (WAV recommended)
2. Transcribe speech → text using **Whisper (local)**
3. Translate text to English if user selects “Other Language”
4. Use the text prompt to generate an image using **Stable Diffusion v1.5 (local)**
5. Display and save the generated image automatically

All models run through local Python libraries such as:
- `openai-whisper`
- `diffusers`
- `Helsinki-NLP` translation pipeline
- `Flask` backend
- `HTML/CSS/JS` frontend

This project is lightweight and perfect for ML portfolios.

---

## 🖼 Screenshot

![Screenshot](images/output.png)

## 📂 Folder Structure

├── app.py

├── requirements.txt

├── templates/

│ └── index.html

├── static/

│ ├── style.css

│ ├── script.js

│ └── images/

│ └── screenshot.png

├── generated/

│ └── (auto-saved images)

└── README.md


---

## ⚙️ Requirements

- Python 3.9 or above  
- FFmpeg installed (for Whisper audio processing)  
- CPU supported (GPU optional)  
- About 10GB of free RAM recommended for Stable Diffusion  

Install FFmpeg from: https://ffmpeg.org/download.html

---

## 📦 Installing Dependencies

###  1. Create a virtual environment

**PowerShell**

```powershell
python -m venv venv
venv/scripts/sctivate
```

###  2. Install required libraries

**PowerShell**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

###  3. Running the project

**PowerShell**

```powershell
python app.py
```

###  4. You will see

**PowerShell**

```powershell
http://127.0.0.1:5000
```

## 🎤 How to Use

1. Upload Speech

      Click Choose File → Upload .wav audio.

2. Choose Language

      English → Direct transcription

      Other Language → Auto-translation to English

3. Click Transcribe

      Whisper produces your text.

4. Click Generate Image

      Stable Diffusion generates an image based on the prompt.

5. View Result

      Image appears on screen and is saved inside /generated.

## Future Scope

- Use of better models for whisper in place of base Ex: large-v3
- For image generations : use Flux diffusers or Google API keys.
- GPU supports more than CPU

## Licesnse

Free to use for personal and educational purposes.
