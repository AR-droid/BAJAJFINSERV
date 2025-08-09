from flask import Flask, request, jsonify
from transformers import pipeline
import requests
import pdfplumber
import io
import os
import re

app = Flask(__name__)

try:
    # Load QA pipeline with default framework (PyTorch or TensorFlow)
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
except ImportError as e:
    print(f"Error loading pipeline: {e}")
    qa_pipeline = None

MAX_CHUNK_SIZE = 4500  # approx chars per chunk

def chunk_text(text, max_size=MAX_CHUNK_SIZE):
    """Split text into chunks no longer than max_size, preferably on sentence boundaries."""
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

def format_question(question):
    return (
        "You are a helpful assistant. "
        "Read the following document carefully and answer the question accurately. "
        "If the answer is not in the text, respond with 'Answer not found in the document.'\n\n"
        f"Question: {question}"
    )

@app.route("/hackrx/run", methods=["POST"])
def run():
    if qa_pipeline is None:
        return jsonify({"error": "QA pipeline is not initialized."}), 500

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

        chunks = chunk_text(text)

        answers = []
        for question in questions:
            best_answer = None
            best_score = -1
            formatted_question = format_question(question)
            for chunk in chunks:
                result = qa_pipeline(question=formatted_question, context=chunk)
                if result["score"] > best_score:
                    best_score = result["score"]
                    best_answer = result["answer"]
            if not best_answer or best_answer.strip() == "":
                best_answer = "Answer not found in the document."
            answers.append(best_answer)

        return jsonify({"answers": answers})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

