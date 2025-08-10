from flask import Flask, request, jsonify
import spacy
import fitz  # PyMuPDF for PDF reading
import re

app = Flask(__name__)

# Load spaCy model (English small is <15MB and loads instantly)
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def simple_qa(document_text, question):
    # Split doc into sentences
    doc_sentences = list(nlp(document_text).sents)
    question_tokens = set([t.lemma_.lower() for t in nlp(question) if not t.is_stop])

    best_sentence = ""
    best_score = 0

    for sent in doc_sentences:
        sent_tokens = set([t.lemma_.lower() for t in sent if not t.is_stop])
        score = len(question_tokens & sent_tokens)
        if score > best_score:
            best_score = score
            best_sentence = sent.text

    return best_sentence if best_sentence else "Answer not found in document"

@app.route("/hackrx/run", methods=["POST"])
def run_qa():
    data = request.get_json()
    pdf_url = data.get("documents")
    questions = data.get("questions", [])

    # For testing, just download PDF locally first
    import requests, tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_data = requests.get(pdf_url).content
    temp_file.write(pdf_data)
    temp_file.close()

    document_text = extract_text_from_pdf(temp_file.name)

    answers = []
    for q in questions:
        ans = simple_qa(document_text, q)
        answers.append(ans)

    return jsonify({"answers": answers})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


