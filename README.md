# 📄 AI Resume & Cover Letter Generator

An AI-powered web app that generates professional, ATS-friendly resumes and tailored cover letters using **Google Gemini 2.5 Flash** — built with **Streamlit** and exportable as **PDF or Word (.docx)**.

---

## ✨ Features

- **AI Cover Letter Generator** — tailored cover letters based on your job description and background
- **AI Resume Builder** — clean, ATS-optimized resume from your details
- **Experience level selector** — Fresher / Student, 1–3 Years, or 3+ Years (adjusts resume structure automatically)
- **Tone selection** — Professional, Enthusiastic, or Concise for cover letters
- **Inline editing** — review and tweak AI output before downloading
- **Dual export** — download as PDF or Word (.docx)
- **In-app API key input** — paste your key directly in the sidebar; no `.env` required
- **Input validation** — friendly warnings if required fields are missing
- **Automatic model fallback** — falls back to `gemini-2.5-flash-lite` if the primary model is rate-limited
- **Detailed error messages** — clear guidance if the API key is invalid or rate-limited

---

## 🗂 Project Structure

```
ai_resume_generator/
│
├── main.py                  # Main Streamlit app (all logic + UI)
├── requirements.txt         # Python dependencies
├── .env                     # Optional: your API key (never commit this)
├── .gitignore               # Ensures .env is not pushed to GitHub
└── README.md
```

---

## 🚀 Getting Started

### 1. Download / clone the project

Place all files in a folder, e.g. `ai_resume_generator`.

### 2. Rename the files correctly

> ⚠️ **Windows users:** Windows hides file extensions by default.
> Open **File Explorer → View → check "File name extensions"** to see and rename them properly.

| Downloaded file | Rename to |
|---|---|
| `main_2.py` or `main` | `main.py` |
| `_env` or `.env.example` | `.env` *(optional — see step 4)* |

### 3. Install Python & dependencies

Make sure Python 3.9+ is installed. Then open a terminal in your project folder and run:

```bash
pip install -r requirements.txt
```

### 4. Set up your API key (two options — pick one)

**Option A — In-app (easiest, no file editing needed):**
Just run the app and paste your Gemini API key directly into the sidebar when prompted.

**Option B — `.env` file:**
Open `.env` in a text editor and replace `your_gemini_api_key_here` with your actual key:
```
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
```
> ⚠️ No quotes, no spaces around `=`, file must be named exactly `.env` (not `.env.txt`)
>
> In Notepad: File → Save As → select **All Files** → type `.env`

Get a free API key at: https://aistudio.google.com/app/apikey

### 5. Run the app

```bash
streamlit run main.py
```

The app opens at `http://localhost:8501`.

---

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Your Google Gemini API key (optional if using in-app input) |

> ⚠️ **Never push your `.env` file to GitHub.** It's listed in `.gitignore`.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `google-generativeai` | Gemini API SDK |
| `python-docx` | Generate Word documents |
| `reportlab` | Generate PDF files |
| `python-dotenv` | Load `.env` variables |

> Note: The `requests` package is **not** required — it is not used in the app.

---

## 🛠 Usage Guide

### Cover Letter Generator
1. Fill in your name, job title, company, and job description
2. Describe your background and key skills
3. Choose a tone (Professional / Enthusiastic / Concise)
4. Click **Generate Cover Letter**
5. Edit the result inline if needed
6. Download as PDF or Word

### Resume Builder
1. Select your experience level (Fresher / 1–3 Years / 3+ Years)
2. Fill in your personal details, experience, education, projects, and skills
3. Click **Generate Resume**
4. Edit the result inline if needed
5. Download as PDF or Word

---

## 🤖 AI Model

The app uses **`gemini-2.5-flash`** as the primary model, with automatic fallback to **`gemini-2.5-flash-lite`** if rate-limited.

> `gemini-2.0-flash` was retired by Google in early 2026.

Free tier limits: **10 requests/minute**, **500 requests/day**.

---

## 🐛 Troubleshooting

| Error | Fix |
|---|---|
| `Streamlit requires raw Python (.py) files` | Rename your file to `main.py` (check extensions are visible in File Explorer) |
| `API key not valid` | Get a fresh key at https://aistudio.google.com/app/apikey — paste it in the sidebar |
| `GOOGLE_API_KEY not found` | Use the sidebar input instead — no `.env` needed |
| `Model not found (404)` | The app auto-falls back to `gemini-2.5-flash-lite` — if both fail, re-download `main.py` |
| `Rate limit (429)` | The app waits 10 s and retries automatically; if it persists, wait 1–2 minutes |

---

## ⚙️ Known Limitations

- PDF formatting is plain text (no columns or graphics) — intentionally ATS-safe
- Output quality depends on the detail you provide in input fields
- Gemini API has free-tier rate limits (10 requests/minute, 500/day)

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) — AI generation (`gemini-2.5-flash`)
- [Streamlit](https://streamlit.io/) — UI framework
- [ReportLab](https://www.reportlab.com/) — PDF generation
- [python-docx](https://python-docx.readthedocs.io/) — Word document generation
