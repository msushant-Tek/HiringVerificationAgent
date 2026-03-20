# Agentic Hiring System - Verify Agent API

The **Verify Agent API** is a core component of the Agentic Hiring System, dedicated to verifying candidate identities, resumes, and technical skills. It leverages an asynchronous processing queue to ingest candidate documents (such as resumes) and external profiles (LinkedIn, GitHub) to generate a comprehensive Trust Score Report through fact-checking and AI analysis.

## Features

- **Document Processing**: Extracts text and relevant information from uploaded resumes using OCR and AI services.
- **Asynchronous Verification**: Background processing of candidate data to ensure the API remains responsive.
- **Fact-Checking**: Evaluates the candidate's claims against provided GitHub and LinkedIn profiles to generate a Trust Score.
- **Report Generation**: Provides a detailed Trust Score Report upon completion of the verification process.

## Tech Stack

- **Python 3**
- **FastAPI** (Web framework)
- **Uvicorn** (ASGI server)
- **Pydantic** (Data validation)
- **Google GenAI / OpenAI** (LLM integrations for text analysis and fact checking)

## Directory Structure

``` text
HiringVerificationAgent/
├── requirements.txt         # Project dependencies
└── src/                     # Source code
    ├── api/                 # API routers and endpoints
    │   └── routes.py
    ├── core/                # Core business logic
    │   └── fact_checker.py  # AI Fact-checking implementation
    ├── integrations/        # 3rd party integrations (e.g. OCR)
    ├── models/              # Pydantic data models (TrustScoreReport, etc.)
    └── main.py              # FastAPI application entrypoint
```

## Setup & Installation

1. **Clone the repository and CD into the project directory:**
   ```bash
   git clone <repository_url>
   cd HiringVerificationAgent
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add the necessary configuration parameters (such as your LLM API keys):
   ```dotenv
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_google_genai_api_key
   ```

## Running the API

Start the development server using `uvicorn`:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
Alternatively, you can run `python src/main.py`.

The API will be available at `http://localhost:8000`.
You can access the interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

## API Endpoints

### 1. Health Check
- **`GET /health`**
- Returns the health status of the service.

### 2. Analyze Candidate
- **`POST /api/v1/verify/analyze`**
- Ingests candidate data and starts an asynchronous verification job.
- **Payload (Form Data):**
  - `candidate_name`: The name of the candidate.
  - `linkedin_url` (Optional): LinkedIn profile URL.
  - `github_handle` (Optional): GitHub username.
  - `resume`: The resume file (PDF/Docx/Image).
- **Response:** Returns a `job_id` and status `202 Accepted`.

### 3. Get Verification Report
- **`GET /api/v1/verify/report/{job_id}`**
- Retrieves the parsed Trust Score Report for a specific job.
- **Response:** Contains the job status (`pending`, `processing_document`, `fact_checking`, `completed`, or `failed`). If completed, includes the detailed result of the verification.
