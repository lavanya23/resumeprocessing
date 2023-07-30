
import PyPDF2
from flask import Flask, request, jsonify
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return None

def preprocess_text(text):
    tokens = text.lower().split()
    return tokens

def calculate_similarity(job_requirements, candidate_qualifications):
    job_requirements = preprocess_text(job_requirements)
    candidate_qualifications = preprocess_text(candidate_qualifications)

    common_tokens = set(job_requirements) & set(candidate_qualifications)
    similarity = len(common_tokens) / len(job_requirements)

    return similarity

@app.route('/process_candidates', methods=['POST'])
def process_candidates():
    try:
        job_requirements = request.form['job_requirements']
        candidate_files = request.files.getlist('candidate_files')

        if not job_requirements:
            return jsonify({"error": "Job requirements not provided."}), 400

        if not candidate_files:
            return jsonify({"error": "No candidate resumes uploaded."}), 400

        results = []

        for candidate_file in candidate_files:
            candidate_resume_text = extract_text_from_pdf(candidate_file)
            if candidate_resume_text:
                similarity = calculate_similarity(job_requirements, candidate_resume_text)
                result = {
                    "candidate": candidate_file.filename,
                    "similarity": similarity
                }
                results.append(result)
            else:
                return jsonify({"error": "Failed to extract text from the candidate's resume."}), 500

        # Sort the results based on similarity in descending order
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred.", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)