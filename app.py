from flask import Flask, request, jsonify
import requests
import fitz   # PyMuPDF
import io
import tempfile
import re
import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

app = Flask(__name__)

# Load spaCy model once at startup
# Make sure en_core_web_sm is installed (Dockerfile does this)
nlp = spacy.load("en_core_web_sm")

MAX_SENTENCES = 4000      # safety cap on sentences to consider
MAX_TOP_SENTENCES = 40    # reduce candidate sentences to top-K by simple relevance
MIN_TOKEN_OVERLAP = 1     # minimal overlap to be considered relevant

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF (fitz)."""
    text = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def sentence_score_map(document_text: str, question: str):
    """
    Return list of (sentence_text, score) where score = number of non-stopword lemma overlaps.
    This is fast and effective for many policy-type documents.
    """
    # small cleaning
    question = question.strip()
    if not question:
        return []

    qdoc = nlp(question.lower())
    q_tokens = {tok.lemma_ for tok in qdoc if (not tok.is_stop and tok.is_alpha)}
    if not q_tokens:
        # fallback to words
        q_tokens = {tok.text.lower() for tok in qdoc if tok.is_alpha}

    doc = nlp(document_text)
    sentences = list(doc.sents)[:MAX_SENTENCES]

    scored = []
    for sent in sentences:
        s_tokens = {tok.lemma_ for tok in sent if (not tok.is_stop and tok.is_alpha)}
        if not s_tokens:
            s_tokens = {tok.text.lower() for tok in sent if tok.is_alpha}
        overlap = len(q_tokens & s_tokens)
        scored.append((sent.text.strip(), overlap))

    # sort by overlap desc
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

def simple_qa(document_text: str, question: str) -> str:
    """
    Find the highest scoring sentence(s) and return best match.
    If nothing relevant, return a polite fallback.
    """
    scored = sentence_score_map(document_text, question)
    if not scored:
        return "I cannot find the answer in the document."

    # take top N candidates (fast)
    top = scored[:MAX_TOP_SENTENCES]
    # best candidate
    best_sentence, best_score = top[0]
    if best_score < MIN_TOKEN_OVERLAP:
        return "I cannot find the answer in the document."
    return best_sentence

@app.route("/hackrx/run", methods=["POST"])
def run_hackrx():
    """
    Expected JSON:
    {
      "documents": "<url-to-pdf>",
      "questions": ["q1", "q2", ...]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    pdf_url = data.get("documents") or data.get("document")  # accept either key
    questions = data.get("questions") or data.get("question")  # accept either key

    if not pdf_url or not questions:
        return jsonify({"error": "Please provide 'documents' (URL) and 'questions' (list) in JSON body"}), 400

    if not isinstance(questions, list):
        return jsonify({"error": "'questions' must be a list"}), 400

    try:
        # download PDF (stream)
        resp = requests.get(pdf_url, timeout=20)
        resp.raise_for_status()
        pdf_bytes = resp.content

        # extract text
        text = extract_text_from_pdf_bytes(pdf_bytes)
        if not text.strip():
            return jsonify({"error": "Failed to extract text from PDF"}), 500

        # answer each question quickly
        answers = []
        for q in questions:
            ans = simple_qa(text, q)
            answers.append({"question": q, "answer": ans})

        return jsonify({"answers": answers}), 200

    except requests.exceptions.RequestException as rexc:
        return jsonify({"error": f"Failed to download PDF: {str(rexc)}"}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug False for production; on local you can set debug=True
    app.run(host="0.0.0.0", port=port, debug=False)


