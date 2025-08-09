from flask import Flask, request, jsonify
from transformers import pipeline
import requests
import pdfplumber
import io
import os
from threading import Thread

app = Flask(__name__)

# Load pipeline once app starts
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

MAX_CHUNK_SIZE = 4500

def chunk_text(text, max_size=MAX_CHUNK_SIZE):
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

# Background worker to process the QA and store or log results as needed
def process_qa(pdf_url, questions):
    try:
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        pdf_bytes = io.BytesIO(pdf_response.content)

        with pdfplumber.open(pdf_bytes) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            # You can log or handle this error differently
            print("Failed to extract text from PDF")
            return

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
            if not best_answer or best_answer.strip() == "":
                best_answer = "I cannot find the answer in the document."
            answers.append(best_answer)

        # For example: log answers, store in DB, or send somewhere
        print({"answers": answers})

    except Exception as e:
        print(f"Error in background QA processing: {e}")

@app.route("/hackrx/run", methods=["POST"])
def run():
    data = request.get_json()

    if not data or "documents" not in data or "questions" not in data:
        return jsonify({"error": "Please provide 'documents' (URL) and 'questions' (list) in JSON body"}), 400

    pdf_url = data["documents"]
    questions = data["questions"]

    # Start background thread to process QA
    Thread(target=process_qa, args=(pdf_url, questions), daemon=True).start()

    # Return immediately
    return jsonify({"status": "Processing started"}), 202

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


