# Resume Matcher 🚀

The ultimate AI-powered tool to match resumes with job descriptions, now featuring an advanced **Engine Flow** for professional-grade tailoring and scoring.

## ✨ New Features (v2.0)

### 🧠 Dual-Engine Flow
- **Standard Flow**: Fast, lightweight AI suggestions to improve your resume.
- **Engine Flow (Major Update)**: 
  - Full-system integration with specialized technical scoring.
  - Advanced PDF generation via integrated LaTeX templates.
  - High-latency support for 14b+ LLM models (Llama 3, etc.).

### 🛡️ Resilience & Performance
- **Connection Stability**: Dedicated Next.js Route Handlers with **180-second timeouts** to prevent "socket hang up" errors during heavy AI processing or file uploads.
- **ATS Scoring v2**: Re-engineered scoring algorithm focusing on quantifiable impact, action-oriented language, and smart domain matching.
- **integrated Engine**: Core logic ported directly into the backend for 90% faster internal calls.

## 🚀 Getting Started with Docker

1. **Environment Setup**:
   Create a `.env` file from the template (do not commit!).
   ```bash
   # BACKEND
   OPENAI_API_KEY=...
   OLLAMA_BASE_URL=http://localhost:11434
   ```

2. **Run Everything**:
   ```bash
   docker compose up -d --build
   ```

3. **Access**:
   - Frontend: `http://localhost:8000`
   - Backend API: `http://localhost:8000/api/v1`
   - Documentation: `http://localhost:8000/docs`

## 🛠️ Tech Stack
- **Frontend**: Next.js (App Router), Tailwind CSS
- **Backend**: FastAPI (Python), TinyDB
- **AI Orhcestration**: LiteLLM, Ollama
- **PDF Export**: LaTeX (via Dockerized TeX Live)

## 🤝 Contributing
Feel free to fork and submit PRs. Please ensure `npm run lint` and `pytest` pass before submitting.

---
*Developed with focus on stability and high-performance AI integration.*
