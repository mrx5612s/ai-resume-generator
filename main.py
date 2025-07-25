import streamlit as st
import os
import markdown2
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use free-tier Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_resume(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {str(e)}"

def main():
    st.set_page_config(page_title="AI Resume Generator", layout="wide")
    st.title("🧠 AI Resume Generator")

    st.sidebar.header("User Info")

    name = st.sidebar.text_input("Full Name", key="name")
    email = st.sidebar.text_input("Email", key="email")
    phone = st.sidebar.text_input("Phone Number", key="phone")
    linkedin = st.sidebar.text_input("LinkedIn", key="linkedin")
    github = st.sidebar.text_input("GitHub / Portfolio", key="github")

    st.header("🎯 Career Objective")
    objective = st.text_area("Write a short objective or leave blank for AI-generated")

    st.header("📚 Education")
    edu_count = st.number_input("How many educational qualifications?", min_value=1, max_value=5, value=2, step=1)
    education = []
    for i in range(edu_count):
        st.subheader(f"Qualification {i+1}")
        degree = st.text_input(f"Degree / Qualification {i+1}", key=f"degree_{i}")
        institution = st.text_input(f"Institution {i+1}", key=f"institution_{i}")
        year = st.text_input(f"Year {i+1}", key=f"year_{i}")
        education.append(f"- **{degree}**, {institution} ({year})")

    st.header("💼 Experience / Projects")
    exp_count = st.number_input("How many entries for experience/projects?", min_value=1, max_value=10, value=3, step=1)
    experience = []
    for i in range(exp_count):
        st.subheader(f"Experience / Project {i+1}")
        title = st.text_input(f"Title {i+1}", key=f"title_{i}")
        description = st.text_area(f"Description {i+1}", key=f"description_{i}")
        experience.append(f"**{title}**\n\n{description}")

    st.header("🛠️ Skills")
    skills = st.text_area("List your skills (comma separated)", key="skills")

    st.header("🏆 Achievements / Certifications")
    achievements = st.text_area("List achievements or certifications", key="achievements")

    if st.button("🚀 Generate Resume"):
        prompt = f"""
        Create a professional resume in markdown format using the following details:
        Name: {name}
        Email: {email}
        Phone: {phone}
        LinkedIn: {linkedin}
        GitHub/Portfolio: {github}

        Objective: {objective}

        Education:
        {chr(10).join(education)}

        Experience / Projects:
        {chr(10).join(experience)}

        Skills: {skills}

        Achievements / Certifications:
        {achievements}

        Use a clean, readable format.
        """

        with st.spinner("Generating Resume..."):
            resume_md = generate_resume(prompt)
            resume_html = markdown2.markdown(resume_md)
            st.subheader("📝 Your Resume")
            st.markdown(resume_md, unsafe_allow_html=True)

            st.download_button("📥 Download Markdown", resume_md, file_name="resume.md")

if __name__ == "__main__":
    main()







