# 📄 AI-Powered Resume Analyzer & Career Copilot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-black?style=for-the-badge&logo=json-web-tokens)

An enterprise-grade, full-stack AI application designed to revolutionize the job application process. This platform provides automated ATS (Applicant Tracking System) scoring, AI-driven resume rewriting, dynamic cover letter generation, and mock interview preparation.

Built with a **FastAPI backend** for high-performance processing and a **Streamlit frontend** for a seamless user experience.

---

## 🚀 Core Features

### 🧠 AI & Parsing Engine
* **Intelligent Resume Parsing:** Accurately extracts text, skills, and entities from PDF and DOCX files.
* **ATS Compatibility Scoring:** Evaluates resumes against specific Job Descriptions (JDs) calculating similarity and keyword matches.
* **AI Resume Rewriter:** Automatically enhances bullet points and summaries using advanced LLM prompts for maximum impact.
* **Cover Letter Generator:** Drafts highly tailored cover letters based on the parsed resume and target job description.
* **Interview Prep Module:** Generates potential interview questions and strategies based on candidate profile gaps.

### 🔐 Security & User Management
* **JWT Authentication:** Secure OAuth2 login and registration system.
* **User Dashboard:** Personalized dashboard to track ATS scores, saved resumes, and job matches.
* **Profile Management:** Secure storage of user data and historical analysis.

### 📊 Interactive UI/UX
* **Data Visualization:** Beautiful charts and graphs displaying ATS score breakdowns and skill gaps.
* **Multi-Page App Structure:** Clean navigation across Dashboard, ATS Report, Rewriter, Cover Letter, and Interview pages.

---

## 🛠️ Technology Stack

* **Frontend:** Streamlit, Custom CSS/JS
* **Backend:** Python, FastAPI, Uvicorn
* **Database & Auth:** SQLAlchemy/Pydantic (Schemas), JWT (JSON Web Tokens), OAuth2
* **AI/NLP:** Large Language Models (LLMs), LangChain, Custom Prompt Engineering
* **Document Processing:** PyPDF2, python-docx
* **DevOps:** Docker, Docker Compose

---

## 📁 System Architecture

The project follows a decoupled architecture, separating the client-side Streamlit application from the robust FastAPI backend.

```text
AI-Resume-Analyzer/
├── app/                      # FastAPI Backend Core
│   ├── api/                  # API Routers (auth, resume, ats, jobs)
│   ├── auth/                 # JWT & Hashing Logic
│   ├── database/             # ORM Models & Schemas
│   ├── prompts/              # LLM System Prompts
│   └── services/             # Core Logic (AI, Parsers, Matchers)
├── streamlit_app/            # Streamlit Frontend UI
│   ├── components/           # Reusable UI elements (navbar, sidebar)
│   └── pages/                # Streamlit Pages (Dashboard, Login, etc.)
├── data/                     # Reference Datasets (skills, universities)
├── docs/                     # Technical Documentation
├── docker/                   # Containerization configs
└── tests/                    # Pytest suite
```

---

## 💻 Installation & Setup

### Method 1: Local Development Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Ashii000/AI-Resume-Analyzer-FastAPI-Streamlit-code.git
cd AI-Resume-Analyzer-FastAPI-Streamlit-code
```

**2. Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up Environment Variables:**
Create a `.env` file in the root directory based on `.env.example` (add your LLM API keys, Database URL, and JWT Secret).

**5. Run the Application:**
You will need two terminals to run the backend and frontend simultaneously.

* **Terminal 1 (Backend - FastAPI):**
  ```bash
  uvicorn app.main:app --reload
  ```
  *API Docs available at: `http://localhost:8000/docs`*

* **Terminal 2 (Frontend - Streamlit):**
  ```bash
  streamlit run streamlit_app/Home.py
  ```
  *App available at: `http://localhost:8501`*

### Method 2: Docker Setup

For a hassle-free setup, you can use Docker Compose to spin up the entire stack.

```bash
cd docker
docker-compose up --build
```

---

## 🧪 Testing

The repository includes a comprehensive test suite covering APIs, authentication, document parsing, and database logic.
Run the tests using Pytest:

```bash
pytest tests/
```

---

## 📄 Documentation

For deeper technical insights, please refer to the `docs/` folder:
* [API Documentation](docs/API.md)
* [System Architecture](docs/Architecture.md)
* [Database Schema](docs/Database.md)

---

## 🤝 Contributing

Contributions are always welcome! If you have ideas for new features or find a bug, please open an issue or submit a pull request.
