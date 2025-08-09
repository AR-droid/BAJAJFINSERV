from flask import Flask, request, jsonify
from transformers import pipeline
import requests
import pdfplumber
import io
import os

app = Flask(__name__)

try:
    # Load QA pipeline with TensorFlow backend
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad", framework="tf")
except ImportError as e:
    # If tensorflow not installed or pipeline loading fails
    print(f"Error loading pipeline with TensorFlow backend: {e}")
    qa_pipeline = None

MAX_CHUNK_SIZE = 4500  # approx chars per chunk; adjust if needed

def chunk_text(text, max_size=MAX_CHUNK_SIZE):
    """Split text into chunks no longer than max_size, on sentence boundaries if possible."""
    import re
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current_chunk = ""
    for sent in sentences:
        if len(current_chunk) + len(sent) + 1 <= max_size:
            current_chunk += " " + sent if current_chunk else sent
        else:
            chunks.append(current_chunk)
            current_chunk = sent
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

@app.route("/hackrx/run", methods=["POST"])
def run():
    if qa_pipeline is None:
        return jsonify({"error": "QA pipeline is not initialized. TensorFlow might not be installed."}), 500

    data = request.get_json()

    if not data or "documents" not in data or "questions" not in data:
        return jsonify({"error": "Please provide 'documents' (URL) and 'questions' (list) in JSON body"}), 400

    pdf_url = data["documents"]
    questions = data["questions"]

    try:
        # Download PDF
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        pdf_bytes = io.BytesIO(pdf_response.content)

        # Extract text from PDF
        with pdfplumber.open(pdf_bytes) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return jsonify({"error": "Failed to extract text from PDF"}), 500

        # Chunk text for QA
        chunks = chunk_text(text)

        answers = []
        for question in questions:
            best_answer = None
            best_score = -1
            for chunk in chunks:
                result = qa_pipeline(question=question, context=chunk)
                if result["score"] > best_score:
                    best_score = result["score"]
                    best_answer = result["answer"]
            if best_answer is None or best_answer.strip() == "":
                best_answer = "I cannot find the answer in the document."
            answers.append(best_answer)

        return jsonify({"answers": answers})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

