
# 🎤 Interview Analyzer

An AI-powered interview practice platform that lets users record spoken answers, transcribes them automatically, and provides structured feedback on confidence, clarity, and relevance.

Built to help students and professionals improve interview performance through measurable insights and actionable suggestions.

---

## ✨ Features

- 🎙️ Record interview answers directly in the browser  
- 🧠 Automatic speech-to-text transcription  
- 📊 Scores for confidence, clarity, and relevance (0–10 scale)  
- 💡 Actionable feedback and improvement tips  
- 🔁 Mock mode for testing without backend  
- ⚡ Fast and lightweight interface  

---

## 🧩 How It Works

1. User enters an interview question.  
2. User records their spoken answer.  
3. Audio is sent to the backend for transcription.  
4. The transcript is analyzed using linguistic heuristics.  
5. Scores and feedback are returned and displayed in the UI.

---

## 🛠 Tech Stack

| Layer      | Technology |
|-----------|-----------|
Frontend    | Streamlit |
Backend     | FastAPI |
Speech      | SpeechRecognition (Google API) |
Audio       | sounddevice, pydub |
Language    | Python |
Deployment  | Local / Cloud-ready |

---

## 📂 Project Structure

interview_analyzer/
├── backend/
│   └── server.py
├── frontend/
│   └── app.py
├── requirements.txt
├── README.md

---

## 🚀 Installation

### Clone the repository

git clone https://github.com/Jashanjindal/Interview-analyzer.git
cd Interview-analyzer

---

## ▶️ Run Locally

### Backend

cd backend
uvicorn server:app --reload

### Frontend

cd frontend
streamlit run app.py

---

## 🔮 Future Improvements

- User login and history tracking  
- Visual analytics dashboard  
- Cloud deployment  
- AI-based feedback  

---

## 👤 Author

Jashan Jindal  
GitHub: https://github.com/Jashanjindal


