import streamlit as st
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from dotenv import load_dotenv
import google.generativeai as genai
from io import BytesIO
from datetime import datetime
today = datetime.now().strftime("%B %d, %Y")

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate AI content
def generate_with_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

# Download as PDF using ReportLab
def download_pdf(text, filename):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 1 * inch
    text_object = c.beginText()
    text_object.setTextOrigin(margin, height - margin)
    text_object.setFont("Helvetica", 12)

    # Wrap and write each line
    max_width = width - 2 * margin
    for line in text.split('\n'):
        wrapped_lines = []
        words = line.strip().split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 12) < max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)

        for wline in wrapped_lines:
            text_object.textLine(wline)
        text_object.textLine("")  # Line break between paragraphs

    c.drawText(text_object)
    c.setTitle(filename.replace(".pdf", ""))
    c.showPage()
    c.save()
    buffer.seek(0)

    st.download_button(
        label="Download as PDF",
        data=buffer,
        file_name=filename,
        mime='application/pdf'
    )

# Download as DOCX
def download_docx(content, filename):
    doc = Document()
    for para in content.split('\n'):
        doc.add_paragraph(para.strip())
    doc_io = BytesIO()
    doc.save(doc_io)
    st.download_button(
        label="Download Word File",
        data=doc_io.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# Sidebar selection
st.sidebar.title("AI Resume & Cover Letter Generator")
option = st.sidebar.radio("Select Tool", ["Cover Letter Generator", "Resume Builder"])

# Cover Letter Generator
if option == "Cover Letter Generator":
    st.title("AI Cover Letter Generator")
    name = st.text_input("Your Name")
    job_title = st.text_input("Job Title")
    company_name = st.text_input("Company Name")
    job_description = st.text_area("Paste the Job Description")
    user_info = st.text_area("Tell me about yourself (skills, experience, etc.)")

    if st.button("Generate Cover Letter"):
        with st.spinner("Generating..."):
           prompt = f"""
Write a tailored and professional cover letter.
Date: {today}
Job Title: {job_title}
Company: {company_name}
Job Description: {job_description}

Candidate Details:
Name: {name}
Background: {user_info}

Output Requirements:
- Do not use any placeholders (like [Your Address] or [mention project...])
- Infer reasonable, contextually relevant details if any data is missing
- Keep it formal, powerful, and concise

Return ONLY the final letter — fully filled and polished.
"""

        result = generate_with_gemini(prompt)
        st.subheader("Generated Cover Letter")
        st.write(result)
        download_pdf(result, f"{name}_cover_letter.pdf")
        download_docx(result, f"{name}_cover_letter.docx")

# Resume Builder
elif option == "Resume Builder":
    st.title("AI Resume Builder")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")
    summary = st.text_area("Professional Summary")
    education = st.text_area("Education")
    experience = st.text_area("Work Experience")
    projects = st.text_area("Projects")
    skills = st.text_area("Skills")
    certifications = st.text_area("Certifications / Achievements")

    if st.button("Generate Resume"):
        with st.spinner("Generating Resume with AI..."):
            prompt = f"""
Generate a professional resume based on the following details. Use proper formatting, sections, and bullet points.

Name: {name}
Email: {email}
Phone: {phone}
LinkedIn: {linkedin}
GitHub: {github}
Summary: {summary}
Education: {education}
Work Experience: {experience}
Projects: {projects}
Skills: {skills}
Certifications: {certifications}

Ensure the formatting is ATS-friendly, clean, and professional.
Avoid any placeholders like [Your Name] or [Date]. Fill all info as if it's complete.
"""
            result = generate_with_gemini(prompt)
            st.subheader("Generated Resume")
            st.write(result)
            download_pdf(result, f"{name}_resume.pdf")
            download_docx(result, f"{name}_resume.docx")

