# 📊 Financial Document Analyzer  

An AI-powered system for analyzing financial documents using **FastAPI**, **Celery**, **Redis**, **MongoDB**, and **CrewAI agents**.  
This project processes uploaded financial documents asynchronously and generates structured investment insights, risk assessments, and verification reports.  

---

## 🚀 Features  
- 📂 **Upload & Analyze** financial documents (PDFs).  
- ⚡ **Asynchronous Processing** with Celery + Redis (no blocking API).  
- 🧠 **AI-Driven Insights** using CrewAI agents:  
  - **Financial Analyst** – Market and document insights.  
  - **Investment Advisor** – Investment opportunities.  
  - **Risk Assessor** – Risk evaluation.  
  - **Verifier** – Document integrity and compliance.  
- 🗄️ **MongoDB Integration** – Store and retrieve results.  
- 🌐 **FastAPI REST API** with Swagger UI for testing.  

---

## 🐞 Bugs Found & Fixes  

### 1. **Celery Worker Crashing on Windows**  
- **Bug**: `billiard` pool caused `WinError 5: Access Denied`.  
- **Fix**: Used `--pool=solo --concurrency=1` for Windows compatibility.  

### 2. **File Not Found (`NA` path issue)**  
- **Bug**: CrewAI agent tried to analyze with `"path": "NA"`.  
- **Fix**: Ensured `file_path` is passed correctly to the task before cleanup.  

### 3. **Duplicate File Cleanup Error**  
- **Bug**: Uploaded file was removed too early, before Celery task read it.  
- **Fix**: Moved cleanup logic to **inside Celery task** (after analysis).  

### 4. **Validation Errors (Empty Query)**  
- **Bug**: Missing query caused FastAPI validation error.  
- **Fix**: Defaulted query to `"Analyze this financial document for investment insights"`.  

---

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-gayatritech/financial-document-analyzer.git
cd financial-document-analyzer


### 2️⃣ Create Virtual Environment


python -m venv .venv
.venv\Scripts\activate   # Windows

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Configure Environment Variables

### 🔑 Environment Setup
1. Copy `.env.example` → `.env`
2. Replace placeholder values with your real credentials
3. Save and restart the app

GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini/gemini-2.0-flash
SERPER_API_KEY=your-serper-api-key
REDIS_HOST=your-redis-host
REDIS_PORT=your-redis-port
REDIS_PASSWORD=your-redis-password
MONGO_URI=your-mongo-uri

### 5️⃣Run Services
uvicorn main:app --reload --port 8000

### Start Celery Worker

celery -A celery_config.celery_app worker --loglevel=info --pool=solo --concurrency=1


✅ API Endpoints

POST /analyze → Upload document + query for analysis

GET /task/{task_id} → Check task status

GET /results/{session_id} → Get results by session

GET /results → Fetch all stored results




 








