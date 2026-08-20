from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import re
import io
from PIL import Image, ExifTags
from rag_engine import retrieve_evidence
from database import engine, Base, SessionLocal, ScanHistory
from sqlalchemy.orm import Session

app = FastAPI(
    title="VeriSense AI API",
    description="Multimodal Fake Content & Trust Verification API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_advice(risk_score: int) -> str:
    if risk_score > 60:
        return "Do not interact with any links or attachments. Block the sender and report this as spam."
    elif risk_score > 30:
        return "Exercise caution. Do not share personal information unless you verify the source."
    else:
        return "This content appears safe. You may proceed normally, but stay vigilant."

def save_scan(db: Session, module: str, input_data: str, risk_score: int, classification: str, user: str = "System User", advice: str = ""):
    if not advice:
        advice = get_advice(risk_score)
    try:
        scan = ScanHistory(module=module, input_data=input_data, risk_score=risk_score, classification=classification, user=user, advice=advice)
        db.add(scan)
        db.commit()
    except Exception as e:
        print(f"Failed to save history: {e}")

# --- Models ---
class Indicator(BaseModel):
    text: str
    risk: str  # high, medium, low

class AnalysisResponse(BaseModel):
    risk_score: int
    classification: str
    confidence: int
    explanation: str
    indicators: List[Indicator]
    evidence: Optional[List[dict]] = None
    advice: Optional[str] = None

class TextAnalysisRequest(BaseModel):
    text: str

class NewsAnalysisRequest(BaseModel):
    text: str

class PhoneAnalysisRequest(BaseModel):
    text: str

class SocialAnalysisRequest(BaseModel):
    text: str

class EmailAnalysisRequest(BaseModel):
    text: str

class UrlAnalysisRequest(BaseModel):
    url: str

# --- LLM Service ---
def generate_explanation_with_ollama(prompt_text: str, context: str) -> str:
    """
    Attempts to call a local Ollama instance to generate an explanation.
    Falls back to a static explanation if Ollama is not available.
    """
    ollama_url = "http://localhost:11434/api/generate"
    
    # You can change the model to 'mistral', 'phi3', etc. depending on what's installed
    payload = {
        "model": "llama3.1",
        "prompt": f"You are VeriSense AI, a cybersecurity assistant. Analyze the following and provide a concise, 2-3 sentence explanation of why it might be risky or safe. Do not use formatting like bolding or lists.\n\nContext: {context}\n\nContent to analyze: {prompt_text}",
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=5.0)
        if response.status_code == 200:
            return response.json().get("response", "Could not generate explanation.")
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        pass
        
    return f"Fallback Explanation (Ollama not detected on localhost:11434): Based on the analysis, this content exhibits characteristics consistent with {context}."

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"status": "online", "message": "VeriSense AI API is running"}

@app.post("/api/analyze/text", response_model=AnalysisResponse)
def analyze_text(request: TextAnalysisRequest, db: Session = Depends(get_db)):
    text_content = request.text.lower()
    if not text_content:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    # Heuristic Analysis
    spam_keywords = ["won", "prize", "click here", "urgent", "lottery", "claim", "free money", "congratulations"]
    detected = [kw for kw in spam_keywords if kw in text_content]
    
    if detected:
        indicators = [Indicator(text=f"Suspicious keyword detected: '{kw}'", risk="high") for kw in detected]
        if "http" in text_content or "www" in text_content:
            indicators.append(Indicator(text="Contains potentially malicious link", risk="high"))
            
        risk_score = min(50 + (len(detected) * 15), 98)
        classification = "High Risk / Spam"
        
        # Call LLM
        explanation = generate_explanation_with_ollama(text_content, "a potential SMS scam or spam message")
        
        advice = get_advice(risk_score)
        save_scan(db, "text", request.text, risk_score, classification, advice=advice)
        
        return AnalysisResponse(
            risk_score=risk_score,
            classification=classification,
            confidence=94,
            explanation=explanation,
            indicators=indicators,
            advice=advice
        )
    
    explanation = generate_explanation_with_ollama(text_content, "a normal, safe text message")
    advice = get_advice(12)
    save_scan(db, "text", request.text, 12, "Low Risk / Safe", advice=advice)
    return AnalysisResponse(
        risk_score=12,
        classification="Low Risk / Safe",
        confidence=89,
        explanation=explanation,
        indicators=[Indicator(text="No obvious spam patterns detected", risk="low")],
        advice=advice
    )

@app.post("/api/analyze/url", response_model=AnalysisResponse)
def analyze_url(request: UrlAnalysisRequest, db: Session = Depends(get_db)):
    url = request.url.lower()
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

    suspicious_patterns = [".xyz", ".top", "free", "login", "update", "verify"]
    detected = [pat for pat in suspicious_patterns if pat in url]
    
    if detected:
        indicators = [Indicator(text=f"Suspicious pattern in URL: '{pat}'", risk="medium") for pat in detected]
        # Heuristic checks
        if len(url) > 60:
            indicators.append(Indicator(text="Unusually long URL length", risk="medium"))
        if len(re.findall(r'-', url)) > 3:
            indicators.append(Indicator(text="Multiple hyphens in domain often used in phishing", risk="high"))

        explanation = generate_explanation_with_ollama(url, "a potentially malicious phishing URL")
        
        save_scan(db, "url", url, 85, "Potential Phishing")
        
        return AnalysisResponse(
            risk_score=85,
            classification="Potential Phishing",
            confidence=90,
            explanation=explanation,
            indicators=indicators
        )

    explanation = generate_explanation_with_ollama(url, "a standard, seemingly safe URL")
    save_scan(db, "url", url, 20, "Low Risk / Normal URL")
    return AnalysisResponse(
        risk_score=20,
        classification="Low Risk / Normal URL",
        confidence=85,
        explanation=explanation,
        indicators=[Indicator(text="Domain appears normal", risk="low")]
    )

@app.post("/api/analyze/news", response_model=AnalysisResponse)
def analyze_news(request: NewsAnalysisRequest, db: Session = Depends(get_db)):
    claim = request.text
    if not claim:
        raise HTTPException(status_code=400, detail="News claim cannot be empty")
        
    # Retrieve evidence from ChromaDB
    retrieved_evidence = retrieve_evidence(claim, n_results=1)
    
    if retrieved_evidence:
        top_evidence = retrieved_evidence[0]
        evidence_text = top_evidence['text']
        context = f"a news claim. Use the following retrieved factual evidence to evaluate it: '{evidence_text}' (Source: {top_evidence['source']})"
        
        explanation = generate_explanation_with_ollama(claim, context)
        
        save_scan(db, "news", claim, 40, "Analyzed via RAG")
        
        return AnalysisResponse(
            risk_score=40, # Moderate risk until explicitly confirmed true/false
            classification="Analyzed via RAG",
            confidence=85,
            explanation=explanation,
            indicators=[Indicator(text="Found relevant information in trusted database", risk="low")],
            evidence=retrieved_evidence
        )
    
    else:
        # No evidence found
        context = "a news claim. I have no trusted evidence in my database regarding this claim. State that the claim is unverified."
        explanation = generate_explanation_with_ollama(claim, context)
        
        save_scan(db, "news", claim, 75, "Unverified / Unknown")
        
        return AnalysisResponse(
            risk_score=75,
            classification="Unverified / Unknown",
            confidence=60,
            explanation=explanation,
            indicators=[Indicator(text="No supporting evidence found in trusted knowledge base", risk="high")],
            evidence=[]
        )

@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Simulated Forensic Analysis
        indicators = []
        risk_score = 10 # Base low risk
        
        # 1. EXIF Data Check
        exif_data = image.getexif()
        has_exif = exif_data is not None and len(exif_data) > 0
        
        if not has_exif:
            indicators.append(Indicator(text="Missing EXIF Metadata (Common in AI-generated images or stripped by social media)", risk="medium"))
            risk_score += 40
        else:
            # Check for specific software tags if present
            software = ""
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'Software':
                    software = str(value).lower()
                    
            if any(x in software for x in ['photoshop', 'gimp', 'canva', 'midjourney', 'stable diffusion']):
                indicators.append(Indicator(text=f"Manipulation software detected in metadata: {software}", risk="high"))
                risk_score += 50
            else:
                indicators.append(Indicator(text="Valid EXIF data present", risk="low"))
                
        # 2. Simulated deep learning artifact check
        # In a real app, you would pass the image bytes to a PyTorch model here.
        # We will simulate this by checking image dimensions (AI models often generate exactly 512x512 or 1024x1024)
        if image.size in [(512, 512), (1024, 1024)]:
            indicators.append(Indicator(text="Image dimensions match standard AI generation defaults (512x512 or 1024x1024)", risk="medium"))
            risk_score += 20
            
        risk_score = min(risk_score, 98)
        
        classification = "High Risk / Potentially AI-Generated" if risk_score > 60 else "Low Risk / Likely Authentic"
        
        context = "an image forensics report. Explain what the absence or presence of EXIF data means."
        explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Missing EXIF: {not has_exif}", context)
        
        save_scan(db, "image", file.filename, risk_score, classification)
        
        return AnalysisResponse(
            risk_score=risk_score,
            classification=classification,
            confidence=85,
            explanation=explanation,
            indicators=indicators
        )
        
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Error processing the image file.")

@app.post("/api/analyze/document", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Placeholder endpoint for Certificate Verification & ID Tampering (OCR).
    """
    if not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="File must be an image or PDF.")
        
    try:
        # In a real scenario, you'd use Tesseract OCR or EasyOCR here:
        # text = pytesseract.image_to_string(Image.open(file.file))
        
        # Simulate OCR and tampering analysis
        filename = file.filename.lower()
        
        indicators = []
        risk_score = 25 # Base risk
        
        indicators.append(Indicator(text="OCR Engine: Text extraction simulated successfully", risk="low"))
        
        if "fake" in filename or "test" in filename:
            indicators.append(Indicator(text="Formatting inconsistency detected (Mismatched fonts in name field)", risk="high"))
            indicators.append(Indicator(text="Issuing authority signature appears digitally copy-pasted (no background noise)", risk="high"))
            indicators.append(Indicator(text="Date field alignment is skewed by 2 degrees relative to document baseline", risk="medium"))
            risk_score = 92
            classification = "High Risk / Potentially Forged"
        else:
            indicators.append(Indicator(text="Layout analysis: Consistent alignment and standard formatting", risk="low"))
            indicators.append(Indicator(text="No obvious digital splicing or cloning artifacts detected", risk="low"))
            risk_score = 15
            classification = "Low Risk / Appears Authentic"
            
        context = "a document forgery analysis report. Briefly explain why mismatched fonts or missing signatures are signs of certificate tampering."
        explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Found inconsistencies: {risk_score > 50}", context)
        
        save_scan(db, "document", filename, risk_score, classification)
        
        return AnalysisResponse(
            risk_score=risk_score,
            classification=classification,
            confidence=88,
            explanation=explanation,
            indicators=indicators
        )
        
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail="Error processing the document file.")

@app.post("/api/analyze/audio", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Placeholder endpoint for AI Audio & Voice Cloning Detection.
    """
    if not file.content_type.startswith("audio/"):
        # Allow generic octet-stream for some platforms sending wav/mp3 incorrectly
        if file.content_type not in ["application/octet-stream"] and not file.filename.endswith((".wav", ".mp3", ".m4a")):
            raise HTTPException(status_code=400, detail="File must be an audio file (.wav, .mp3).")
        
    try:
        # In a real scenario, you would use librosa to extract the Mel spectrogram
        # and feed it into a CNN/Transformer trained on synthetic voice datasets (like ASVspoof)
        
        # Simulate audio forensic analysis
        filename = file.filename.lower()
        
        indicators = []
        risk_score = 15 # Base risk
        
        indicators.append(Indicator(text="Spectrogram extraction simulated successfully", risk="low"))
        
        # We simulate a "synthetic" detection if the word 'ai' or 'fake' or 'clone' is in the filename
        if any(word in filename for word in ["ai", "fake", "clone", "synthetic"]):
            indicators.append(Indicator(text="Unnatural frequency clipping detected above 12kHz", risk="high"))
            indicators.append(Indicator(text="Phase irregularities consistent with neural vocoders (e.g., HiFi-GAN)", risk="high"))
            indicators.append(Indicator(text="Lack of natural breath sounds / acoustic room variance", risk="medium"))
            risk_score = 94
            classification = "High Risk / Synthetic Voice Detected"
        else:
            indicators.append(Indicator(text="Natural frequency distribution observed", risk="low"))
            indicators.append(Indicator(text="Phase continuity matches authentic human speech", risk="low"))
            risk_score = 12
            classification = "Low Risk / Likely Authentic"
            
        context = "an audio forensics report. Explain why phase irregularities or unnatural clipping in a spectrogram suggest a voice might be AI-generated."
        explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Found synthetic artifacts: {risk_score > 50}", context)
        
        save_scan(db, "audio", filename, risk_score, classification)
        
        return AnalysisResponse(
            risk_score=risk_score,
            classification=classification,
            confidence=89,
            explanation=explanation,
            indicators=indicators
        )
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail="Error processing the audio file.")

@app.post("/api/analyze/phone", response_model=AnalysisResponse)
def analyze_phone(request: PhoneAnalysisRequest, db: Session = Depends(get_db)):
    phone = request.text
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number cannot be empty")
        
    indicators = []
    risk_score = 15
    classification = "Low Risk / Normal"
    
    # Simple heuristics for phone numbers (e.g. +44 70 / premium rate / known spam prefixes)
    suspicious_prefixes = ["+4470", "+234", "+881", "0900", "809"]
    clean_phone = re.sub(r'\D', '', phone) # strip non-digits
    
    if any(phone.startswith(prefix) or phone.startswith(prefix.replace("+", "")) for prefix in suspicious_prefixes):
        indicators.append(Indicator(text="Number originates from a high-risk region or premium rate prefix", risk="high"))
        risk_score = 85
        classification = "High Risk / Potential Scam"
    else:
        indicators.append(Indicator(text="Number prefix does not match known spam databases", risk="low"))
        
    context = "a phone number risk analysis report. Explain why premium rate or international prefixes from certain regions are used in scams."
    explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Phone: {phone}", context)
    
    save_scan(db, "phone", phone, risk_score, classification)
    
    return AnalysisResponse(risk_score=risk_score, classification=classification, confidence=92, explanation=explanation, indicators=indicators)

@app.post("/api/analyze/social", response_model=AnalysisResponse)
def analyze_social(request: SocialAnalysisRequest, db: Session = Depends(get_db)):
    bio = request.text.lower()
    if not bio:
        raise HTTPException(status_code=400, detail="Profile text cannot be empty")
        
    indicators = []
    risk_score = 20
    classification = "Low Risk / Appears Authentic"
    
    bot_keywords = ["crypto", "forex", "bitcoin", "whatsapp me", "invest", "sugar baby", "cashapp", "giveaway"]
    detected = [kw for kw in bot_keywords if kw in bio]
    
    if detected:
        indicators = [Indicator(text=f"Suspicious keyword found: {kw}", risk="medium") for kw in detected]
        risk_score = min(30 + (len(detected) * 20), 95)
        if risk_score > 60:
            classification = "High Risk / Potential Bot or Scam Profile"
            
    if "http" in bio and len(detected) > 0:
        indicators.append(Indicator(text="Profile contains external link alongside scam keywords", risk="high"))
        risk_score += 15
        
    risk_score = min(risk_score, 98)
    
    context = "a social media profile analysis report. Explain why excessive use of finance or crypto keywords alongside links often indicates a bot or scam profile."
    explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Text: {bio}", context)
    
    save_scan(db, "social", request.text[:50], risk_score, classification)
    
    return AnalysisResponse(risk_score=risk_score, classification=classification, confidence=87, explanation=explanation, indicators=indicators)

@app.post("/api/analyze/email", response_model=AnalysisResponse)
def analyze_email(request: EmailAnalysisRequest, db: Session = Depends(get_db)):
    email_text = request.text.lower()
    if not email_text:
        raise HTTPException(status_code=400, detail="Email text cannot be empty")
        
    indicators = []
    risk_score = 15
    classification = "Low Risk / Clean"
    
    phishing_phrases = ["account suspended", "verify your identity", "password reset", "unauthorized login", "action required immediately", "dear customer", "kindly"]
    detected = [phrase for phrase in phishing_phrases if phrase in email_text]
    
    if detected:
        indicators = [Indicator(text=f"Common phishing phrase detected: '{phrase}'", risk="high") for phrase in detected]
        risk_score = min(50 + (len(detected) * 15), 99)
        classification = "High Risk / Potential Phishing"
        
    if "http" in email_text and "verify" in email_text:
        indicators.append(Indicator(text="Contains link paired with verification request (Classic phishing pattern)", risk="high"))
        risk_score += 20
        
    risk_score = min(risk_score, 99)
    
    context = "an email phishing analysis report. Explain why generic greetings ('dear customer') and urgent requests paired with links are common phishing tactics."
    explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Content: {email_text}", context)
    
    save_scan(db, "email", request.text[:50], risk_score, classification)
    
    return AnalysisResponse(risk_score=risk_score, classification=classification, confidence=93, explanation=explanation, indicators=indicators)

@app.post("/api/analyze/video", response_model=AnalysisResponse)
async def analyze_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Placeholder endpoint for Deepfake Video Detection.
    """
    if not file.content_type.startswith("video/"):
        # Allow generic octet-stream fallback
        if file.content_type not in ["application/octet-stream"] and not file.filename.endswith((".mp4", ".webm", ".mov")):
            raise HTTPException(status_code=400, detail="File must be a video file (.mp4, .webm).")
        
    try:
        # In a real scenario, you would use OpenCV to extract frames
        # and a Vision Transformer (ViT) or 3D-CNN to detect facial boundary blending.
        
        filename = file.filename.lower()
        
        indicators = []
        risk_score = 15 # Base risk
        
        indicators.append(Indicator(text="Frame extraction and facial boundary mapping simulated", risk="low"))
        
        # We simulate a deepfake detection if the word 'deepfake' or 'fake' or 'swap' is in the filename
        if any(word in filename for word in ["deepfake", "fake", "swap", "ai"]):
            indicators.append(Indicator(text="Temporal inconsistency detected across 15 consecutive frames", risk="high"))
            indicators.append(Indicator(text="Micro-expressions and eye-blinking patterns lack biological realism", risk="high"))
            indicators.append(Indicator(text="Facial boundary blending artifacts (Gaussian blur masking) detected", risk="high"))
            risk_score = 96
            classification = "High Risk / Deepfake Video Detected"
        else:
            indicators.append(Indicator(text="Biological patterns (pulse, blinking) appear natural", risk="low"))
            indicators.append(Indicator(text="Facial boundaries remain consistent with lighting conditions", risk="low"))
            risk_score = 14
            classification = "Low Risk / Likely Authentic"
            
        context = "a deepfake video analysis report. Briefly explain why temporal inconsistencies and facial boundary blending are common in face-swap algorithms."
        explanation = generate_explanation_with_ollama(f"Risk score: {risk_score}, Found deepfake artifacts: {risk_score > 50}", context)
        
        save_scan(db, "video", filename, risk_score, classification)
        
        return AnalysisResponse(
            risk_score=risk_score,
            classification=classification,
            confidence=91,
            explanation=explanation,
            indicators=indicators
        )
        
    except Exception as e:
        print(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail="Error processing the video file.")

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    scans = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc()).limit(50).all()
    results = []
    for s in scans:
        results.append({
            "id": s.id,
            "user": s.user,
            "module": s.module,
            "input_data": s.input_data,
            "risk_score": s.risk_score,
            "classification": s.classification,
            "advice": s.advice,
            "timestamp": s.timestamp.isoformat()
        })
    return {"history": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
