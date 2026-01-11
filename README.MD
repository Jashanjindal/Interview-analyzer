🎤 Interview Analyzer

An AI-powered interview practice platform that lets users record spoken answers, transcribes them automatically, and provides structured feedback on confidence, clarity, and relevance.

Built to help students and professionals improve interview performance through measurable insights and actionable suggestions.

✨ Features

🎙️ Record interview answers directly in the browser

🧠 Automatic speech-to-text transcription

📊 Scores for confidence, clarity, and relevance (0–10 scale)

💡 Actionable feedback and improvement tips

🔁 Mock mode for testing without backend

⚡ Fast and lightweight interface

🧩 How It Works

User enters an interview question.

User records their spoken answer.

Audio is sent to the backend for transcription.

The transcript is analyzed using linguistic heuristics.

Scores and feedback are returned and displayed in the UI.

🛠 Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	FastAPI
Speech	SpeechRecognition (Google API)
Audio	sounddevice, pydub
Language	Python
Deployment	Local / Cloud-ready
📂 Project Structure
interview_analyzer/
├── backend/
│   └── server.py
├── frontend/
│   └── app.py
├── requirements.txt
├── README.md

🚀 Installation
1️⃣ Clone the repository
git clone https://github.com/Jashanjindal/Interview-analyzer.git
cd Interview-analyzer

2️⃣ (Optional but recommended) Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

▶️ Run Locally
Start Backend (FastAPI)
cd backend
uvicorn server:app --reload


Backend runs at:

http://127.0.0.1:8000

Start Frontend (Streamlit)

Open new terminal:

cd frontend
streamlit run app.py


App runs at:

http://localhost:8501

🧪 Example

Input Question:

Tell me about yourself


Output:

Confidence: 8.2 / 10

Clarity: 7.5 / 10

Relevance: 8.0 / 10

Feedback:

Use fewer filler words

Add more specific examples

Structure answers using STAR method

🔮 Future Improvements

User login and history tracking

Visual analytics dashboard

Cloud deployment (AWS / GCP)

AI-based feedback using LLMs

Resume + Interview combined insights

👤 Author

Jashan Jindal
B.Tech (AI & ML) Student
Poet | Developer | Content Creator

GitHub: https://github.com/Jashanjindal
