import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from google import genai
from google.genai import types, errors
import os
from dotenv import load_dotenv
import time
import models
import schemas
from database import engine, get_db

# 1. Initializes the database (creates the tables if they do not exist)
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the FastAPI app
app = FastAPI(title="Smart Support Inbox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In development, it allows calls from any source (e.g. React).
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Load environment variables and Gemini client
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


def analyze_ticket_with_ai(subject: str, body: str):
    """Helper function to analyze a ticket using Gemini AI"""
    if not client:
        return {"urgency": "BASSA", "category": "Generale", "suggested_reply": "API Key non configurata."}

    prompt = f"""
    You are an AI customer support assistant. Analyze the following support ticket.
    
    Subject: "{subject}"
    Body: "{body}"
    
    Return your response EXCLUSIVELY as valid JSON matching this exact structure:
    {{
      "urgency": "ALTA" | "MEDIA" | "BASSA",
      "category": "Category Name (e.g., Authentication, Billing, Bug, General)",
      "suggested_reply": "A professional and empathetic draft reply to send to the customer (in Italian)"
    }}
    """
    
    # Parametri per il Retry
    MAX_RETRIES = 3  # maximum number of attempts
    INITIAL_DELAY = 2  # initial seconds of waiting

    for attempt in range(MAX_RETRIES):
        try:
            chat = client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            response = chat.send_message(prompt)
            return json.loads(response.text)
        except Exception as e:
            # Se siamo all'ultimo tentativo, logghiamo l'errore e usiamo la Graceful Degradation (Fallback)
            if attempt == MAX_RETRIES - 1:
                print(f"Errore definitivo dopo {MAX_RETRIES} tentativi: {e}")
                return {
                    "urgency": "MEDIA",
                    "category": "Generale",
                    "suggested_reply": "Impossibile generare una risposta automatica al momento."
            }

            # Calcolo attesa esponenziale: 2s al 1° errore, 4s al 2° errore
            delay = INITIAL_DELAY * (2 ** attempt)
            print(f"Tentativo {attempt + 1} fallito ({e}). Riprovo tra {delay} secondi...")
            time.sleep(delay)


@app.get("/")
def home():
    return {"message": "Smart Support Inbox API è attiva!"}


@app.post("/tickets/", response_model=schemas.TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    """It creates a new ticket, automatically analyzes it using AI, and saves it to the database"""
    # AI Analysis
    ai_result = analyze_ticket_with_ai(ticket.subject, ticket.body)

    # DB record creation
    db_ticket = models.Ticket(
        subject=ticket.subject,
        body=ticket.body,
        urgency=ai_result.get("urgency", "MEDIA"),
        category=ai_result.get("category", "Generale"),
        suggested_reply=ai_result.get("suggested_reply", ""),
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets/", response_model=list[schemas.TicketResponse])
def get_tickets(db: Session = Depends(get_db)):
    """Retrieve the list of all saved tickets."""
    return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()