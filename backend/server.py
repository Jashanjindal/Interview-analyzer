from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from typing import Dict, Any
import uvicorn

app = FastAPI(title="Interview Analyzer API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def transcribe_audio(audio_path: str) -> tuple[str, str]:
    """
    Transcribe audio file using speech recognition
    Returns: (transcript, error_message)
    """
    try:
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
            return transcript, None
            
    except sr.UnknownValueError:
        return None, "Could not understand audio"
    except sr.RequestError as e:
        return None, f"Speech recognition error: {str(e)}"
    except Exception as e:
        return None, f"Transcription error: {str(e)}"

def analyze_text(transcript: str, question: str) -> Dict[str, Any]:
    """
    Analyze the interview transcript and provide scores
    """
    words = transcript.split()
    word_count = len(words)
    sentence_count = len([s for s in transcript.split('.') if s.strip()])
    
    
    confidence_score = 5.0
    clarity_score = 5.0
    relevance_score = 5.0
    
    
    confident_words = ['confident', 'definitely', 'certainly', 'absolutely', 'experienced']
    hedging_words = ['maybe', 'perhaps', 'might', 'possibly', 'kind of', 'sort of']
    
    confidence_count = sum(1 for word in confident_words if word in transcript.lower())
    hedging_count = sum(1 for word in hedging_words if word in transcript.lower())
    
    confidence_score += confidence_count * 0.5
    confidence_score -= hedging_count * 0.5
    
    
    if 50 <= word_count <= 150:
        confidence_score += 2
    elif word_count < 30:
        confidence_score -= 1
    
    
    avg_words_per_sentence = word_count / max(sentence_count, 1)
    
    
    if 12 <= avg_words_per_sentence <= 22:
        clarity_score += 2
    
    
    fillers = transcript.lower().count('um') + transcript.lower().count('uh') + transcript.lower().count('like')
    clarity_score -= min(fillers * 0.3, 3)
    
   
    structure_words = ['first', 'second', 'third', 'finally', 'additionally', 'furthermore']
    structure_count = sum(1 for word in structure_words if word in transcript.lower())
    clarity_score += min(structure_count * 0.5, 2)
    
    
    question_words = set(question.lower().split())
    transcript_words = set(transcript.lower().split())
    
    
    common_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for'}
    question_words -= common_words
    
    
    overlap = len(question_words & transcript_words)
    relevance_score += min(overlap * 0.7, 3)
    
    
    example_indicators = ['example', 'instance', 'experience', 'project', 'time when', 'situation']
    if any(indicator in transcript.lower() for indicator in example_indicators):
        relevance_score += 1.5
    
    
    confidence_score = min(max(confidence_score, 0), 10)
    clarity_score = min(max(clarity_score, 0), 10)
    relevance_score = min(max(relevance_score, 0), 10)
    
    
    feedback = []

    
    if confidence_score < 6:
        feedback.append("Use more assertive language and reduce hedging words (maybe, possibly, etc.)")
    elif confidence_score > 8:
        feedback.append("Great confidence in your delivery!")
    
    
    if fillers > 5:
        feedback.append("Reduce filler words (um, uh, like) for better clarity")
    
    if avg_words_per_sentence > 25:
        feedback.append("Try breaking down long sentences into shorter ones for better clarity")
    elif avg_words_per_sentence < 10:
        feedback.append("Consider expanding your sentences with more details")
    
    if structure_count == 0:
        feedback.append("Use transitional phrases (first, second, additionally) to structure your response")
    
    
    if relevance_score < 6:
        feedback.append("Focus more on directly answering the question asked")
    
    if word_count < 50:
        feedback.append("Provide more detailed responses with specific examples")
    elif word_count > 200:
        feedback.append("Keep responses more concise and focused")
    
    
    star_words = {'situation', 'task', 'action', 'result'}
    if not any(word in transcript.lower() for word in star_words):
        feedback.append("Consider using the STAR method: Situation, Task, Action, Result")
    
    
    if not feedback:
        feedback.append("Excellent response! Keep up the good work.")
    
    return {
        "confidence_score": round(confidence_score, 1),
        "clarity_score": round(clarity_score, 1),
        "relevance_score": round(relevance_score, 1),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "feedback": feedback
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Interview Analyzer API is running"}

@app.post("/analyze_audio")
async def analyze_audio(
    audio: UploadFile = File(...),
    question: str = Form(...)
) -> Dict[str, Any]:
    """
    Analyze interview audio
    
    Parameters:
    - audio: Audio file (WAV format)
    - question: The interview question asked
    
    Returns:
    - transcript: Text transcription of the audio
    - analysis: Detailed analysis with scores and feedback
    """
    temp_path = None
    
    try:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await audio.read()
            tmp.write(content)
            temp_path = tmp.name
        
        
        transcript, error = transcribe_audio(temp_path)
        
        if error:
            return {
                "success": False,
                "error": error,
                "transcript": "",
                "analysis": {}
            }
        
        if not transcript:
            return {
                "success": False,
                "error": "No speech detected in audio",
                "transcript": "",
                "analysis": {}
            }
        
        
        analysis = analyze_text(transcript, question)
        
        return {
            "success": True,
            "transcript": transcript,
            "analysis": analysis,
            "question": question
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Server error: {str(e)}",
            "transcript": "",
            "analysis": {}
        }
    
    finally:
        
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

@app.post("/analyze_text")
async def analyze_text_endpoint(
    transcript: str = Form(...),
    question: str = Form(...)
) -> Dict[str, Any]:
    """
    Analyze interview text directly
    
    Parameters:
    - transcript: Text of the interview response
    - question: The interview question asked
    
    Returns:
    - analysis: Detailed analysis with scores and feedback
    """
    try:
        analysis = analyze_text(transcript, question)
        
        return {
            "success": True,
            "transcript": transcript,
            "analysis": analysis,
            "question": question
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis error: {str(e)}",
            "analysis": {}
        }

if __name__ == "__main__":
    print("🚀 Starting Interview Analyzer API...")
    print("📍 API will be available at: http://127.0.0.1:8000")
    print("📚 API documentation: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
