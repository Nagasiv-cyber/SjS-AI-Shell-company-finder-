import os
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase (Mock or Real)
try:
    # Check if creds file exists or use default
    if os.path.exists("firebase_credentials.json"):
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")
    else:
        print("Firebase credentials not found. Using Mock Firestore.")
        db = None
except Exception as e:
    print(f"Firebase init failed: {e}. Using Mock Firestore.")
    db = None

# Initialize Gemini (Mock or Real)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("Gemini AI initialized.")
else:
    print("GEMINI_API_KEY not found. Using Mock Gemini responses.")
    model = None

class GeminiService:
    @staticmethod
    async def generate_text(prompt: str) -> str:
        if model:
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"AI Error: {str(e)}"
        else:
            return GeminiService._get_mock_response(prompt)

    @staticmethod
    def _get_mock_response(prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "typology" in prompt_lower:
             return "Detected circular routing patterns consistent with layered money laundering schemes. Assets are moving through multiple shell entities in high-risk jurisdictions (BVI -> Panama -> Cypus) with no apparent commercial utility."
        if "proximity" in prompt_lower:
            return "Entity is 2-degrees of separation from a known sanctioned individual (SDN-4922) via shared directorship in 'Oceanic Holdings Ltd'."
        if "summary" in prompt_lower:
            return "High-risk indicators detected: Rapid movement of funds to tax havens, lack of physical presence, and shared nominees with known bad actors. This entity behaves like a classic pass-through shell company used for obscuring beneficial ownership."
        if "brief" in prompt_lower:
             return "INTELLIGENCE BRIEF:\n\nSubject shows high-velocity transactions inconsistent with stated business purpose (Consulting). Connections to 'Alpha Shell' (Sanctioned) confirmed via transaction #TX-992. Recommended Action: File SAR immediately."
        return "I have analyzed the available data. The risk indicators suggest potential illicit activity. Please review the transaction logs for further confirmation."

class FirestoreService:
    @staticmethod
    def log_decision(data: dict):
        if db:
            try:
                db.collection('decision_logs').add({
                    **data,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"Firestore Error: {e}")
        else:
            print(f"[MOCK DB] Logged decision: {data}")

    @staticmethod
    def store_case_file(data: dict):
        if db:
            try:
                db.collection('case_files').add({
                    **data,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"Firestore Error: {e}")
        else:
             print(f"[MOCK DB] Stored case file for {data.get('company_name')}")

    @staticmethod
    def suppress_alert(alert_id: str, reason: str):
         if db:
            try:
                # In real app, update alert status
                pass
            except:
                pass
         else:
             print(f"[MOCK DB] Alert {alert_id} suppressed. Reason: {reason}")
