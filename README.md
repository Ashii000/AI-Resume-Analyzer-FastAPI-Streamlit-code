# AI Resume Analyzer & ATS Score Checker

## Project Description

The AI Resume Analyzer & ATS Score Checker is a production-ready, full-stack web application designed to help job seekers evaluate and optimize their resumes against Applicant Tracking System (ATS) criteria. The system leverages a FastAPI backend and a Streamlit front-end to provide document parsing for PDF and DOCX formats, ATS compatibility scoring, and generative AI-assisted resume rewriting.

## Installation Guide

### Step 1: Create and Activate a Virtual Environment

A Python virtual environment isolates project dependencies from the system Python installation.

```bash
python -m venv .venv
```

- On Windows:
  ```bash
  .\.venv\Scripts\activate
  ```
- On macOS / Linux:
  ```bash
  source .venv/bin/activate
  ```

### Step 2: Install Dependencies

Install all required Python packages from the requirements file.

```bash
pip install -r requirements.txt
```

## Setup Instructions

1. Copy the example environment file to create your local configuration.

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set the required secret values.

## Usage Instructions

1. **Initialize and Run the Backend:** Start the FastAPI server and initialize the local database.

   ```bash
   python run.py
   ```

2. **Launch the Front-End:** Open a separate terminal, activate the virtual environment, and start the Streamlit interface.

   ```bash
   streamlit run streamlit_app/Home.py
   ```

3. Access the Streamlit URL in your browser to upload a resume and view the ATS analysis.

## Folder Structure

- `app/` — FastAPI application package, including API routers, service logic, and database models.
- `streamlit_app/` — Streamlit front-end application and UI components.
- `data/` — Static supporting data, such as skills lists and stopword dictionaries.
- `docs/` — Project design documentation and API reference material.
- `docker/` — Dockerfile and docker-compose configuration for containerized deployment.

## Complete List of Dependencies

- `fastapi`
- `streamlit`
- `sqlalchemy`
- `pydantic`
- `sentence-transformers`
- `spacy`
- `uvicorn`
- `jinja2`

## APIs Used

- **Google Gemini API** — Generative AI model used for dynamic resume rewriting and actionable improvement suggestions.

## Libraries/Frameworks Used

- **FastAPI** — Backend web framework for building modular, high-performance RESTful APIs.
- **Streamlit** — Front-end framework for building the interactive resume analysis interface.
- **SQLAlchemy** — Object-Relational Mapping (ORM) library for database interactions.
- **Pydantic** — Used for data validation and schema definition within the FastAPI backend.
- **sentence-transformers** — Used for generating semantic embeddings for resume and job description matching.
- **spaCy** — Used for natural language processing tasks like keyword extraction and text parsing.

## Additional Configuration Required

All configurable parameters are defined through environment variables specified in the `.env` file.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Used to sign and verify JWT authentication tokens. |
| `DATABASE_URL` | Specifies the database connection string, such as `sqlite:///./ai_resume_analyzer.db` for local development. |
| `GEMINI_API_KEY` | Authenticates requests to the Google Gemini API. |
| `BACKEND_HOST` & `BACKEND_PORT` | Network configuration for the backend server, defaulting to `127.0.0.1` and `8000`. |
| `UPLOAD_DIR` | Local path for storing uploaded resumes and files, defaulting to `app/uploads`. |