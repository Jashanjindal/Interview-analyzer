import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import tempfile
import requests
from datetime import datetime

# Configure page
st.set_page_config(page_title="Interview Analyzer", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #1a1a2e;
        color: #eee;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .instruction-box {
        background-color: #16213e;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0f4c75;
    }
    .tip-box {
        background-color: #0f4c75;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "result" not in st.session_state:
    st.session_state.result = None
if "sample_rate" not in st.session_state:
    st.session_state.sample_rate = 44100
if "duration" not in st.session_state:
    st.session_state.duration = 5  # Default 5 seconds

# ---------------- HELPER FUNCTIONS ----------------
def record_audio(duration, sample_rate=44100):
    """Record audio using sounddevice"""
    try:
        st.info(f"🎤 Recording for {duration} seconds... Speak now!")
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='int16')
        sd.wait()
        return recording, sample_rate
    except Exception as e:
        st.error(f"❌ Recording error: {str(e)}")
        return None, None

def save_audio(audio_data, sample_rate):
    """Save audio to temporary file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            scipy.io.wavfile.write(tmp.name, sample_rate, audio_data)
            st.success(f"💾 Audio saved successfully!")
            return tmp.name
    except Exception as e:
        st.error(f"❌ Error saving audio: {str(e)}")
        return None

def mock_analysis(transcript, question):
    """Mock analysis function"""
    word_count = len(transcript.split())
    
    # Calculate scores
    confidence_score = min(10, max(5, word_count / 15))
    clarity_score = min(10, 7 + (1 if len(transcript.split('.')) > 2 else 0))
    relevance_score = min(10, 6 + (2 if any(word in transcript.lower() for word in question.lower().split()) else 0))
    
    feedback = []
    
    if word_count < 30:
        feedback.append("💡 Try to provide more detailed responses (aim for 50-150 words)")
    elif word_count > 200:
        feedback.append("💡 Consider being more concise in your answers")
    else:
        feedback.append("✅ Good response length!")
    
    feedback.append("✅ Good structure and delivery")
    feedback.append("💡 Consider using the STAR method (Situation, Task, Action, Result)")
    feedback.append("🎯 Practice maintaining confident tone throughout")
    
    return {
        "confidence_score": round(confidence_score, 1),
        "clarity_score": round(clarity_score, 1),
        "relevance_score": round(relevance_score, 1),
        "word_count": word_count,
        "feedback": feedback
    }

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    <div class="instruction-box">
    1. Set recording duration (5-60 seconds)<br>
    2. Enter your interview question<br>
    3. Click <b>🎤 Start Recording</b><br>
    4. Speak your answer clearly<br>
    5. Click <b>🔍 Analyze Interview</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    # Recording duration
    st.session_state.duration = st.slider(
        "Recording Duration (seconds)",
        min_value=5,
        max_value=60,
        value=st.session_state.duration,
        step=5
    )
    
    backend_url = st.text_input(
        "Backend URL",
        value="http://127.0.0.1:8000",
        help="URL of your FastAPI backend"
    )
    
    use_mock = st.checkbox(
        "Use Mock Analysis",
        value=True,
        help="Enable this if backend is not available"
    )
    
    st.markdown("---")
    st.markdown("""
    <div class="tip-box">
    💡 <b>Tip:</b> Speak clearly and maintain a steady pace for best results
    </div>
    """, unsafe_allow_html=True)
    
    # Debug info
    with st.expander("🔍 Debug Info"):
        st.write(f"Audio recorded: {st.session_state.audio_data is not None}")
        st.write(f"Audio path: {st.session_state.audio_path}")
        st.write(f"Analysis done: {st.session_state.analysis_done}")
        if st.session_state.audio_data is not None:
            st.write(f"Audio shape: {st.session_state.audio_data.shape}")
            st.write(f"Sample rate: {st.session_state.sample_rate}")

# ---------------- MAIN UI ----------------
st.title("🎤 Interview Analyzer")
st.markdown("---")

# Interview question input
question = st.text_input(
    "📝 Interview Question",
    value="Tell me about yourself",
    placeholder="Enter the interview question here..."
)

st.markdown("### 🎙️ Recording Controls")

# Recording controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎤 Start Recording", type="primary", use_container_width=True):
        st.session_state.audio_data = None
        st.session_state.audio_path = None
        st.session_state.analysis_done = False
        st.session_state.result = None
        
        # Record audio
        audio_data, sample_rate = record_audio(st.session_state.duration)
        
        if audio_data is not None:
            st.session_state.audio_data = audio_data
            st.session_state.sample_rate = sample_rate
            
            # Save audio
            audio_path = save_audio(audio_data, sample_rate)
            if audio_path:
                st.session_state.audio_path = audio_path
            
            st.rerun()

with col2:
    if st.button("🔊 Play Recording", use_container_width=True):
        if st.session_state.audio_path:
            try:
                with open(st.session_state.audio_path, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error(f"Error playing audio: {str(e)}")
        else:
            st.warning("⚠️ No recording available. Record first!")

with col3:
    if st.button("🗑️ Clear Recording", use_container_width=True):
        st.session_state.audio_data = None
        st.session_state.audio_path = None
        st.session_state.analysis_done = False
        st.session_state.result = None
        st.info("🔄 Recording cleared")
        st.rerun()

# Status display
if st.session_state.audio_data is not None:
    duration = len(st.session_state.audio_data) / st.session_state.sample_rate
    st.success(f"✅ Recording complete! Duration: {duration:.2f} seconds")
else:
    st.info("⏺️ Press 'Start Recording' to begin")

st.markdown("---")

# Display audio player
if st.session_state.audio_path:
    st.markdown("### 🔊 Recorded Audio")
    try:
        with open(st.session_state.audio_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/wav")
    except Exception as e:
        st.error(f"Error displaying audio: {str(e)}")

# ---------------- ANALYZE ----------------
st.markdown("---")
st.markdown("### 🔍 Analysis")

# Always show the button, but disable if conditions aren't met
can_analyze = st.session_state.audio_path and not st.session_state.analysis_done

if not can_analyze:
    if st.session_state.audio_data is None:
        st.info("⏺️ Record your answer first to enable analysis")
    else:
        st.info("⏳ Processing audio... analysis will be available shortly")

if st.button("🔍 Analyze Interview", type="primary", use_container_width=True, disabled=not can_analyze):
    with st.spinner("🧠 Analyzing your response..."):
        try:
            if use_mock:
                # Mock analysis
                import time
                time.sleep(2)  # Simulate processing
                
                mock_transcript = "Thank you for the question. I am a software developer with 5 years of experience in Python and web development. I have worked on multiple projects involving machine learning and data analysis. In my previous role, I led a team to develop a customer analytics platform that improved business insights by 40%. I am passionate about solving complex problems and delivering high-quality solutions. I believe my skills align well with this position."
                
                result = {
                    "success": True,
                    "transcript": mock_transcript,
                    "analysis": mock_analysis(mock_transcript, question),
                    "question": question
                }
                st.session_state.result = result
                st.session_state.analysis_done = True
                st.rerun()
                
            else:
                # Call backend
                with open(st.session_state.audio_path, "rb") as f:
                    res = requests.post(
                        f"{backend_url}/analyze_audio",
                        data={"question": question},
                        files={"audio": ("recording.wav", f, "audio/wav")},
                        timeout=60
                    )
                    
                    if res.status_code == 200:
                        result = res.json()
                        st.session_state.result = result
                        st.session_state.analysis_done = True
                        st.rerun()
                    else:
                        st.error(f"Backend error: {res.status_code} - {res.text}")
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Enable 'Use Mock Analysis' in Settings")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ---------------- DISPLAY RESULTS ----------------
if st.session_state.analysis_done and st.session_state.result:
    result = st.session_state.result
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Transcript
    st.markdown("### 📝 Transcript")
    transcript = result.get("transcript", "No transcript available")
    st.info(transcript)
    
    # Analysis
    analysis = result.get("analysis", {})
    
    if isinstance(analysis, dict) and analysis:
        # Scores
        st.markdown("### 📈 Performance Scores")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            confidence = analysis.get("confidence_score", 0)
            st.metric("💪 Confidence", f"{confidence}/10")
        
        with col2:
            clarity = analysis.get("clarity_score", 0)
            st.metric("🎯 Clarity", f"{clarity}/10")
        
        with col3:
            relevance = analysis.get("relevance_score", 0)
            st.metric("✅ Relevance", f"{relevance}/10")
        
        with col4:
            word_count = analysis.get("word_count", 0)
            st.metric("📊 Words", word_count)
        
        # Feedback
        st.markdown("### 💡 Feedback & Suggestions")
        feedback_items = analysis.get("feedback", [])
        
        if feedback_items:
            for tip in feedback_items:
                st.markdown(f"- {tip}")
        else:
            st.write("No specific feedback available")
        
        # Overall
        avg_score = (confidence + clarity + relevance) / 3
        st.markdown("### 🎓 Overall Assessment")
        
        if avg_score >= 8:
            st.success(f"**Excellent!** (Average: {avg_score:.1f}/10)")
            st.balloons()
        elif avg_score >= 6:
            st.info(f"**Good!** (Average: {avg_score:.1f}/10)")
        else:
            st.warning(f"**Needs Improvement** (Average: {avg_score:.1f}/10)")
        
        # Try Again button
        if st.button("🔄 Try Another Question", use_container_width=True):
            st.session_state.audio_data = None
            st.session_state.audio_path = None
            st.session_state.analysis_done = False
            st.session_state.result = None
            st.rerun()
    else:
        st.error("❌ No analysis data available")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Interview Analyzer v2.0 | Built with Streamlit & sounddevice</div>",
    unsafe_allow_html=True
)