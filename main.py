import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai
from io import BytesIO
from datetime import datetime

# ─── Page Setup ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Resume & Cover Letter Generator",
    page_icon="📄",
    layout="centered",
)

today = datetime.now().strftime("%B %d, %Y")

# ─── API Key Handling ─────────────────────────────────────────────────────────

load_dotenv()
env_key = os.getenv("GOOGLE_API_KEY", "").strip()

st.sidebar.title("📄 AI Career Tools")
st.sidebar.markdown("Powered by **Gemini 2.5 Flash**")

if env_key and not env_key.startswith("your_"):
    api_key = env_key
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 API Key Required")
    st.sidebar.markdown(
        "Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)"
    )
    sidebar_key = st.sidebar.text_input(
        "Paste your Gemini API key",
        type="password",
        placeholder="AIzaSy...",
        help="Your key is never stored — it only lives in this browser session.",
    )
    api_key = sidebar_key.strip() if sidebar_key else ""

if not api_key:
    st.info(
        "👈 **Paste your Gemini API key in the sidebar to get started.**\n\n"
        "Get a free key at: https://aistudio.google.com/app/apikey"
    )
    st.stop()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ Failed to configure Gemini: {e}")
    st.stop()

st.sidebar.markdown("---")
option = st.sidebar.radio("Select Tool", ["Cover Letter Generator", "Resume Builder"])
st.sidebar.markdown("---")
st.sidebar.info("Fill in the fields, click Generate, then download your document.")

# ─── Markdown Cleaner ─────────────────────────────────────────────────────────

def clean_markdown(text: str) -> str:
    """
    Strip all markdown so PDF/DOCX don't show raw asterisks, hashes, or
    AI 'thinking out loud' lines like (Implicit from Python...).
    """
    # Remove bold/italic markers like **text** or *text*
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove inline code backticks
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Remove markdown headers (##, ###) — keep the text
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove AI meta-commentary lines
    bad_patterns = [
        r"^\(implicit.*\)",
        r"^\(inferred.*\)",
        r"^\(note:.*\)",
        r"^\(assuming.*\)",
        r"^\(potentially.*\)",
        r"^\[.*\]$",          # bare [placeholder] lines
        r"^potentially .*",
        r"^assuming .*",
    ]

    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip().lower()
        if any(re.match(p, stripped) for p in bad_patterns):
            continue
        cleaned.append(line)

    return "\n".join(cleaned)

# ─── AI Generation ────────────────────────────────────────────────────────────

def generate_with_gemini(prompt: str) -> str | None:
    """
    Uses gemini-2.5-flash — the current free-tier model as of April 2026.
    gemini-2.0-flash was retired by Google in early 2026.
    Free tier: 10 RPM / 500 requests per day.
    """
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    max_retries = 2

    for model_name in models_to_try:
        current_model = genai.GenerativeModel(model_name)

        for attempt in range(1, max_retries + 1):
            try:
                response = current_model.generate_content(prompt)
                return response.text

            except Exception as e:
                err = str(e)

                if "API_KEY_INVALID" in err or ("400" in err and "API_KEY" in err):
                    st.error(
                        "❌ **Invalid API key.**\n\n"
                        "Go to https://aistudio.google.com/app/apikey, "
                        "delete the old key, create a brand-new one, and paste it in the sidebar."
                    )
                    return None

                elif "404" in err or "deprecated" in err.lower() or (
                    "not found" in err.lower() and "model" in err.lower()
                ):
                    break  # try next model

                elif "429" in err or "quota" in err.lower() or "RESOURCE_EXHAUSTED" in err:
                    if attempt < max_retries:
                        with st.spinner(f"⏳ Rate limit on {model_name} — waiting 10s..."):
                            time.sleep(10)
                        continue
                    else:
                        break  # try next model

                else:
                    st.error(f"❌ Gemini error (model: {model_name}): {err}")
                    return None

    st.error(
        "❌ **Could not generate a response.**\n\n"
        "**Fix options:**\n"
        "1. Wait 1–2 minutes and try again (free tier: 10 requests/min)\n"
        "2. Check your quota at https://aistudio.google.com/app/apikey\n"
        "3. Add a billing account — free to add, you only pay beyond free limits"
    )
    return None

# ─── PDF Export ───────────────────────────────────────────────────────────────

def build_pdf(text: str) -> BytesIO:
    """Render plain text into a well-formatted PDF with bullet and header support."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 0.85 * inch
    max_width = width - 2 * margin
    body_size = 10.5
    header_size = 12
    line_height = body_size * 1.55

    y = height - margin

    def new_page():
        nonlocal y
        c.showPage()
        y = height - margin

    def draw_wrapped(text_to_draw, font, size, x_start):
        nonlocal y
        words = text_to_draw.split()
        if not words:
            return
        avail = max_width - (x_start - margin)
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if c.stringWidth(test, font, size) < avail:
                current = test
            else:
                if y < margin + line_height:
                    new_page()
                c.setFont(font, size)
                c.drawString(x_start, y, current)
                y -= line_height
                current = word
                avail = max_width  # continuation lines use full width
                x_start = margin
        if current.strip():
            if y < margin + line_height:
                new_page()
            c.setFont(font, size)
            c.drawString(x_start, y, current)
            y -= line_height

    c.setFont("Helvetica", body_size)

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()

        # Blank line
        if not stripped:
            y -= line_height * 0.35
            if y < margin:
                new_page()
            continue

        # Section header: ALL CAPS short line
        is_header = stripped.isupper() and 3 < len(stripped) < 65

        if is_header:
            y -= line_height * 0.25
            if y < margin + line_height * 2:
                new_page()
            c.setFont("Helvetica-Bold", header_size)
            c.drawString(margin, y, stripped)
            y -= line_height * 0.3
            # Underline rule
            c.setLineWidth(0.6)
            c.line(margin, y + line_height * 0.55, width - margin, y + line_height * 0.55)
            y -= line_height * 0.45

        # Bullet line
        elif stripped.startswith("- "):
            bullet_text = stripped[2:]
            bullet_x = margin + 0.12 * inch
            text_x = margin + 0.22 * inch
            if y < margin + line_height:
                new_page()
            c.setFont("Helvetica", body_size)
            c.drawString(bullet_x, y, "•")
            draw_wrapped(bullet_text, "Helvetica", body_size, text_x)

        # Normal line
        else:
            draw_wrapped(stripped, "Helvetica", body_size, margin)

    c.save()
    buffer.seek(0)
    return buffer


def download_pdf(text: str, filename: str):
    try:
        buffer = build_pdf(text)
        st.download_button(
            label="📄 Download as PDF",
            data=buffer,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# ─── DOCX Export ──────────────────────────────────────────────────────────────

def build_docx(content: str) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    for para in content.split("\n"):
        line = para.strip()
        if not line:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            continue

        is_header = line.isupper() and 3 < len(line) < 65
        is_bullet = line.startswith("- ")

        if is_header:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(12)
            run.font.name = "Calibri"
            # Bottom border (underline the whole paragraph)
            pPr = p._p.get_or_add_pPr()
            pBdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "4")
            bottom.set(qn("w:space"), "1")
            bottom.set(qn("w:color"), "auto")
            pBdr.append(bottom)
            pPr.append(pBdr)

        elif is_bullet:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(line[2:])
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)

        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(line)
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)

    doc_io = BytesIO()
    doc.save(doc_io)
    return doc_io.getvalue()


def download_docx(content: str, filename: str):
    try:
        data = build_docx(content)
        st.download_button(
            label="📝 Download as Word (.docx)",
            data=data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"DOCX generation failed: {e}")

# ─── Input Validation ─────────────────────────────────────────────────────────

def validate_fields(**fields) -> bool:
    missing = [label for label, val in fields.items() if not val.strip()]
    if missing:
        st.warning(f"⚠️ Please fill in: {', '.join(missing)}")
        return False
    return True

# ─── Cover Letter Generator ───────────────────────────────────────────────────

if option == "Cover Letter Generator":
    st.title("✉️ AI Cover Letter Generator")
    st.markdown("Generate a tailored, professional cover letter in seconds.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Full Name *", placeholder="e.g. Priya Sharma")
        company_name = st.text_input("Company Name *", placeholder="e.g. Google")
    with col2:
        job_title = st.text_input("Job Title *", placeholder="e.g. Software Engineer")
        tone = st.selectbox("Tone", ["Professional", "Enthusiastic", "Concise"])

    job_description = st.text_area(
        "Paste the Job Description *",
        placeholder="Copy and paste the full job description here...",
        height=180,
    )
    user_info = st.text_area(
        "About You (skills, experience, achievements) *",
        placeholder="e.g. 3 years of Python experience, built a REST API serving 10k users...",
        height=130,
    )

    if st.button("🚀 Generate Cover Letter", type="primary", use_container_width=True):
        if validate_fields(
            **{
                "Full Name": name,
                "Job Title": job_title,
                "Company Name": company_name,
                "Job Description": job_description,
                "About You": user_info,
            }
        ):
            prompt = f"""You are a professional career coach and expert cover letter writer.

Write a tailored, compelling cover letter for the candidate below.

Date: {today}
Job Title: {job_title}
Company: {company_name}
Tone: {tone}

Job Description:
{job_description}

Candidate:
Name: {name}
Background: {user_info}

STRICT RULES — follow every one without exception:
1. Output ONLY the final letter text. Absolutely no commentary, preamble, or notes before or after.
2. Do NOT use any markdown formatting — no asterisks, no hashes, no backticks, no **bold** markers whatsoever.
3. Do NOT use placeholders like [Your Address], [City], [Date], [mention X], [your project].
4. Do NOT write your own reasoning, assumptions, or parenthetical notes anywhere.
5. Use plain paragraphs separated by blank lines. Nothing else.
6. Structure: greeting → strong opening → why you're the fit → 1-2 specific achievements → closing CTA.
7. Address as "Dear Hiring Manager," if no contact name given.
8. Keep to 3-4 short punchy paragraphs — human-sounding, not robotic or generic.
"""
            with st.spinner("✨ Writing your cover letter..."):
                result = generate_with_gemini(prompt)

            if result:
                result = clean_markdown(result)
                st.success("✅ Cover letter generated!")
                st.markdown("---")
                st.subheader("Your Cover Letter")
                edited = st.text_area("Review & edit before downloading:", value=result, height=400)
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    download_pdf(edited, f"{name.replace(' ', '_')}_cover_letter.pdf")
                with col2:
                    download_docx(edited, f"{name.replace(' ', '_')}_cover_letter.docx")

# ─── Resume Builder ───────────────────────────────────────────────────────────

elif option == "Resume Builder":
    st.title("📋 AI Resume Builder")
    st.markdown("Build an ATS-friendly, professional resume instantly.")
    st.markdown("---")

    st.subheader("Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="Priya Sharma")
        email = st.text_input("Email *", placeholder="priya@example.com")
        phone = st.text_input("Phone *", placeholder="+91 98765 43210")
    with col2:
        linkedin = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/priya")
        github = st.text_input("GitHub URL", placeholder="github.com/priya")
        job_target = st.text_input("Target Job Title *", placeholder="Data Scientist")

    st.subheader("Professional Content")

    experience_level = st.radio(
        "Experience Level",
        ["Fresher / Student", "1–3 Years Experience", "3+ Years Experience"],
        horizontal=True,
    )

    summary = st.text_area(
        "Professional Summary *",
        placeholder="e.g. Final year B.Tech student with hands-on Python and ML project experience, seeking a Data Science role.",
        height=90,
    )
    experience = st.text_area(
        "Work Experience / Internships",
        placeholder="Fresher? List internships or write 'None'.\ne.g. ML Intern at XYZ Corp (June–Aug 2024) — built sentiment analysis model, 87% accuracy",
        height=120,
    )
    education = st.text_area(
        "Education *",
        placeholder="e.g. B.Tech Computer Science, GCET, 2024–Present, CGPA: 8.2",
        height=80,
    )
    projects = st.text_area(
        "Projects",
        placeholder="e.g. AI Resume Generator — Python, Streamlit, Gemini API — generates ATS-friendly resumes; 50+ test users",
        height=110,
    )
    skills = st.text_area(
        "Skills *",
        placeholder="Python, SQL, Pandas, NumPy, Scikit-learn, Git, Streamlit",
        height=70,
    )
    certifications = st.text_area(
        "Certifications / Achievements",
        placeholder="e.g. Google Data Analytics Certificate, Kaggle Intro to ML, Hackathon runner-up",
        height=70,
    )

    if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
        if validate_fields(
            **{
                "Full Name": name,
                "Email": email,
                "Phone": phone,
                "Target Job Title": job_target,
                "Summary": summary,
                "Education": education,
                "Skills": skills,
            }
        ):
            contact_parts = [email, phone]
            if linkedin:
                contact_parts.append(linkedin)
            if github:
                contact_parts.append(github)
            contact_line = " | ".join(contact_parts)

            is_fresher = "Fresher" in experience_level

            prompt = f"""You are an expert resume writer. Write a professional, ATS-optimized resume.

Experience level: {experience_level}
Target Role: {job_target}

Candidate details:
Name: {name}
Contact: {contact_line}
Summary: {summary}
Work Experience / Internships: {experience if experience.strip() else "None"}
Education: {education}
Projects: {projects if projects.strip() else "None provided"}
Skills: {skills}
Certifications / Achievements: {certifications if certifications.strip() else "None provided"}

ABSOLUTE OUTPUT RULES — break none of these:
1. Output ONLY the resume. No preamble, no "Here is your resume:", no commentary after.
2. ZERO markdown — no asterisks (*), no hashes (#), no backticks (`), no **bold** markers. None at all.
3. ZERO parenthetical notes — do not write things like (Implicit from Python/SQL: potentially Pandas...) or (inferred) or (assuming) anywhere.
4. ZERO placeholders — no [City], [mention X], [your project name].
5. Use PLAIN TEXT only. Section headers must be in ALL CAPS.
6. Every bullet point must start with "- " (hyphen space).
7. Blank line between each section.
8. Only list skills that were explicitly provided — do not guess or invent tools not mentioned.
9. If a section has no data, omit that section entirely — do not write "None" or "N/A" in the resume.

{"FRESHER RULES (apply since experience level is Fresher/Student):" if is_fresher else ""}
{"- Order: Name/Contact → Summary → Education → Projects → Internships (if any) → Skills → Certifications" if is_fresher else ""}
{"- Make the Projects section detailed and strong — it's the most important section for freshers." if is_fresher else ""}
{"- Each project: name, tech stack used, what you built, and a measurable outcome if possible." if is_fresher else ""}
{"- Do NOT invent experience or add tools not provided by the candidate." if is_fresher else ""}

Begin directly with the candidate's name on line 1.
"""
            with st.spinner("✨ Building your resume..."):
                result = generate_with_gemini(prompt)

            if result:
                result = clean_markdown(result)
                st.success("✅ Resume generated!")
                st.markdown("---")
                st.subheader("Your Resume")
                st.caption("💡 Tip: Add specific numbers and outcomes to make it stronger before downloading.")
                edited = st.text_area("Review & edit before downloading:", value=result, height=500)
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    download_pdf(edited, f"{name.replace(' ', '_')}_resume.pdf")
                with col2:
                    download_docx(edited, f"{name.replace(' ', '_')}_resume.docx")
