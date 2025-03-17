from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from PIL import Image
import pytesseract
from gtts import gTTS
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = "audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extracted_text = pytesseract.image_to_string(Image.open(file_path)).strip()
    if not extracted_text:
        extracted_text = "No readable text found in the image."
    
    audio_file = file.filename.rsplit(".", 1)[0] + ".mp3"
    audio_path = os.path.join(AUDIO_FOLDER, audio_file)

    tts = gTTS(text=extracted_text, lang="en")
    tts.save(audio_path)

    return jsonify({
        "text": extracted_text,
        "audio_url": f"http://127.0.0.1:5000/audio/{audio_file}"
    })

@app.route("/audio/<filename>")
def get_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route("/clear", methods=["DELETE"])
def clear_files():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    image_path = os.path.join(UPLOAD_FOLDER, filename)
    audio_path = os.path.join(AUDIO_FOLDER, filename.rsplit(".", 1)[0] + ".mp3")

    try:
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
