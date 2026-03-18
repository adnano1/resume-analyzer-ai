from flask import Flask, request, render_template
import spacy
import PyPDF2
import re

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_skills(text):
    doc = nlp(text)
    skills = []
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'SKILL']:  # Adjust labels as needed
            skills.append(ent.text)
    # Also extract nouns that might be skills
    for token in doc:
        if token.pos_ == 'NOUN' and len(token.text) > 2:
            skills.append(token.text.lower())
    return list(set(skills))

def calculate_match(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    score = len(matched) / len(job_skills) * 100 if job_skills else 0
    return matched, score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return 'No file uploaded', 400
    file = request.files['resume']
    job_desc = request.form['job']
    
    if file.filename == '':
        return 'No file selected', 400
    
    if file and file.filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(file)
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)
        matched, score = calculate_match(resume_skills, job_skills)
        
        return render_template('result.html', 
                             score=round(score, 2),
                             resume_skills=', '.join(resume_skills),
                             job_skills=', '.join(job_skills),
                             matched=', '.join(matched))
    else:
        return 'Invalid file type. Please upload a PDF.', 400

if __name__ == '__main__':
    app.run(debug=True)