import os
import re
import docx2txt
from pdfminer.high_level import extract_text
# Extraction formation ----done here.
def extract_text_from_resume(file_path):
    """Extracts text from PDF or DOCX resume."""
    if file_path.endswith('.pdf'):
        return extract_text(file_path)
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    return ""
#Keywords connection building here..
def parse_resume(file_path):
    """Parses resume and extracts skills, experience, and education."""
    text = extract_text_from_resume(file_path)

    skills = re.findall(r"(?i)(Python|Java|C\+\+|SQL|Django|Machine Learning|NLP|AI|AWS|Data Structures|Algorithms|DSA)", text)
    experience = re.findall(r"(\d+\+? years? of experience.*?)\n", text)
    education = re.findall(r"(?i)(Bachelor|Master|PhD)[^\n]*", text)

    return {
        "skills": list(set(skills)),
        "experience": experience,
        "education": education
    }
