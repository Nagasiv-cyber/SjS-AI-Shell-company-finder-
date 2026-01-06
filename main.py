from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import networkx as nx

from data_gen import generate_mock_data
from ml_logic import calculate_risk_score
from services import GeminiService, FirestoreService

app = FastAPI(
    title="Shell Company Risk Identification API",
    description="Backend for AI-based ML/TF detection system",
    version="1.0.0"
)

# CORS - Allow all for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
companies_db = []
transactions_db = []
ownerships_db = []
risk_scores_db = {}
alerts_db = []

# --- Request Models ---
class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class AnalysisRequest(BaseModel):
    entity_id: str
    analysis_type: str # 'typology', 'proximity', 'narrative'

class SuppressAlertRequest(BaseModel):
    alert_id: str
    reason: str
    analyst_id: str = "analyst_001"

class CaseFileRequest(BaseModel):
    entity_id: str
    title: str
    notes: str
    included_alerts: List[str]

class SARRequest(BaseModel):
    entity_id: str
    analyst_id: str
    risk_score: float
    justification: str

class EscalationRequest(BaseModel):
    entity_id: str
    analyst_id: str
    jurisdiction: str
    reason: str

class InformerReportRequest(BaseModel):
    reporter_id: str
    entity_name: str
    jurisdiction: str
    nature_of_suspicion: str
    description: str
    cross_border: bool
    accounts_masked: str = None

class ReportReviewRequest(BaseModel):
    report_id: str
    analyst_id: str
    action: str # LINK, DISMISS, CASE
    notes: str = None

class LegalInquiryRequest(BaseModel):
    entity_id: str
    legal_authority: str
    case_context: str

# Mock In-Memory Database for Reports
informer_reports_db = []

# ... (keep existing models)

# --- Startup ---

@app.on_event("startup")
def startup_event():
    global companies_db, transactions_db, ownerships_db, risk_scores_db, alerts_db
    print("Generating synthetic data...")
    companies_db, transactions_db, ownerships_db = generate_mock_data(num_companies=50, num_transactions=300)
    
    # Calculate initial risk scores
    print("Calculating ML risk scores...")
    for comp in companies_db:
        # Filter transactions for this company
        comp_txs = [t for t in transactions_db if t['from_id'] == comp['id'] or t['to_id'] == comp['id']]
        risk_data = calculate_risk_score(comp, comp_txs)
        risk_scores_db[comp['id']] = risk_data
        
        # Generate Alerts based on Critical/High risk
        if risk_data['level'] in ['CRITICAL', 'HIGH']:
            alerts_db.append({
                "id": f"alt_{len(alerts_db)+1}",
                "company_id": comp['id'],
                "company_name": comp['name'],
                "risk_score": risk_data['score'],
                "risk_level": risk_data['level'],
                "reason": risk_data['reasons'][0] if risk_data['reasons'] else "Unknown High Risk",
                "status": "Open",
                "signals": ["Conflict-Zone Routing", "Crypto Off-Ramp"] if risk_data['score'] > 0.9 else [],
                "created_at": "2023-10-27"
            })
            
    print(f"Data ready: {len(companies_db)} companies, {len(alerts_db)} alerts.")

# --- Existing Endpoints ---

@app.get("/")
def read_root():
    return {"status": "System Operational", "message": "AI Risk Detection Engine Online"}

@app.get("/companies")
def get_companies():
    results = []
    for c in companies_db:
        r = risk_scores_db.get(c['id'], {})
        results.append({**c, "risk_score": r.get('score', 0), "risk_level": r.get('level', 'LOW')})
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results

@app.get("/company/{company_id}")
def get_company(company_id: str):
    company = next((c for c in companies_db if c['id'] == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    risk_data = risk_scores_db.get(company_id, {})
    
    # Get recent transactions
    recent_txs = [t for t in transactions_db if t['from_id'] == company_id or t['to_id'] == company_id]
    
    return {
        "company": company,
        "risk_analysis": {
            **risk_data,
            "threat_proximity": "High" if risk_data.get('score', 0) > 0.8 else "Low", 
            "typology": "Layered Networks" if risk_data.get('score', 0) > 0.7 else "Standard Commercial"
        },
        "transactions": recent_txs[:10]
    }

@app.get("/alerts")
def get_alerts():
    return alerts_db

@app.get("/network/{company_id}")
def get_network(company_id: str):
    nodes = []
    links = []
    added_ids = set()
    
    target_comp = next((c for c in companies_db if c['id'] == company_id), None)
    if target_comp:
        nodes.append({"id": target_comp['id'], "label": target_comp['name'], "type": "target"})
        added_ids.add(target_comp['id'])
        
    # Find neighbors via transactions
    related_txs = [t for t in transactions_db if t['from_id'] == company_id or t['to_id'] == company_id]
    
    for tx in related_txs:
        # Determine neighbor ID
        neighbor_id = tx['to_id'] if tx['from_id'] == company_id else tx['from_id']
        
        if neighbor_id not in added_ids:
            neighbor = next((c for c in companies_db if c['id'] == neighbor_id), None)
            if neighbor:
                risk = risk_scores_db.get(neighbor_id, {}).get('level', 'LOW')
                nodes.append({"id": neighbor['id'], "label": neighbor['name'], "type": "neighbor", "risk": risk})
                added_ids.add(neighbor_id)
        
        links.append({
            "source": tx['from_id'],
            "target": tx['to_id'],
            "amount": tx['amount'],
            "type": tx['type'],
            "date": tx['date']
        })

    # Find neighbors via ownership
    related_owns = [o for o in ownerships_db if o['owner_id'] == company_id or o['subsidiary_id'] == company_id]
    
    for own in related_owns:
        neighbor_id = own['subsidiary_id'] if own['owner_id'] == company_id else own['owner_id']
        
        if neighbor_id not in added_ids:
            neighbor = next((c for c in companies_db if c['id'] == neighbor_id), None)
            if neighbor:
                risk = risk_scores_db.get(neighbor_id, {}).get('level', 'LOW')
                nodes.append({"id": neighbor['id'], "label": neighbor['name'], "type": "neighbor", "risk": risk})
                added_ids.add(neighbor_id)
        
        links.append({
            "source": own['owner_id'],
            "target": own['subsidiary_id'],
            "amount": f"{own['percentage']}%",
            "type": "Ownership",
            "date": own['date_acquired']
        })

    return {"nodes": nodes, "links": links}

@app.get("/dashboard/metrics")
def get_metrics():
    high_risk_count = len([c for c in companies_db if risk_scores_db.get(c['id'], {}).get('level') in ['HIGH', 'CRITICAL']])
    return {
        "total_companies": len(companies_db),
        "high_risk_companies": high_risk_count,
        "active_alerts": len(alerts_db),
        "total_transactions_analyzed": len(transactions_db),
        "behavior_stability_index": 87 # Mocked aggregate metric
    }

# --- New AI & Feature Endpoints ---

@app.post("/api/ai/chat")
async def chat_with_ai(request: ChatRequest):
    # Construct a context-aware prompt
    context_str = f"Context: {request.context}" if request.context else ""
    prompt = f"You are a Senior Risk Analyst AI. {context_str}\nUser: {request.message}\nAnswer:"
    response = await GeminiService.generate_text(prompt)
    return {"reply": response}

@app.post("/api/ai/analyze")
async def analyze_entity(request: AnalysisRequest):
    # Fetch entity details to feed to AI
    company = next((c for c in companies_db if c['id'] == request.entity_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    risk_info = risk_scores_db.get(request.entity_id, {})
    
    prompt = f"Analyze dictionary: {company} Risk Level: {risk_info.get('level')}."
    
    if request.analysis_type == 'typology':
        prompt += " Identify the specific money laundering typology (e.g. Circular Routing, Trade-Based) and explain why."
    elif request.analysis_type == 'proximity':
        prompt += " Calculate distinct threat proximity to sanctioned networks based on high risk partners."
    elif request.analysis_type == 'narrative':
        prompt += " Write a 3-sentence executive risk summary for an intelligence report."
        
    result = await GeminiService.generate_text(prompt)
    return {"analysis": result}

@app.post("/api/alerts/suppress")
async def suppress_alert(request: SuppressAlertRequest):
    # Updates in-memory db
    alert = next((a for a in alerts_db if a['id'] == request.alert_id), None)
    if alert:
        alert['status'] = 'Suppressed'
        alert['suppression_reason'] = request.reason
    
    # Log to Firestore
    FirestoreService.log_decision({
        "type": "ALERT_SUPPRESSION",
        "alert_id": request.alert_id,
        "reason": request.reason,
        "analyst": request.analyst_id
    })
    
    return {"status": "success", "message": "Alert suppressed and feedback logged."}

@app.post("/api/reports/create")
async def create_case_file(request: CaseFileRequest):
    # Generate AI summary for the report
    ai_summary = await GeminiService.generate_text(f"Write a comprehensive case file summary for entity {request.entity_id} with title {request.title}. Notes: {request.notes}")
    
    report_data = {
        "entity_id": request.entity_id,
        "title": request.title,
        "notes": request.notes,
        "ai_summary": ai_summary,
        "alerts": request.included_alerts,
        "status": "Draft"
    }
    
    FirestoreService.store_case_file(report_data)
    
    return {"status": "success", "report_id": "cf_new_001", "summary": ai_summary}

@app.post("/api/compliance/sar")
async def create_sar_draft(request: SARRequest):
    # AI Generates the narrative
    narrative = await GeminiService.generate_text(f"Draft a Suspicious Activity Report (SAR) narrative for entity {request.entity_id}. Risk Justification: {request.justification}. Focus on factual risk indicators.")
    
    draft_data = {
        "type": "SAR_DRAFT",
        "entity_id": request.entity_id,
        "narrative": narrative,
        "status": "In Review",
        "created_at": "timestamp_now"
    }
    FirestoreService.log_decision(draft_data) # Log creation
    return {"status": "success", "draft_id": "sar_001", "narrative": narrative}

@app.post("/api/compliance/escalate")
async def create_escalation(request: EscalationRequest):
    # Ensure dual approval logic (simulated)
    brief = await GeminiService.generate_text(f"Write a formal FIU escalation case brief for entity {request.entity_id}. Jurisdiction: {request.jurisdiction}. Reason: {request.reason}.")
    
    escalation_data = {
        "type": "FIU_ESCALATION",
        "entity_id": request.entity_id,
        "brief": brief,
        "status": "Pending Dual Approval",
        "jurisdiction": request.jurisdiction
    }
    FirestoreService.log_decision(escalation_data)
    return {"status": "success", "case_id": "case_fiu_001", "brief": brief}

@app.post("/api/compliance/inquiry")
async def create_legal_inquiry(request: LegalInquiryRequest):
    packet = {
        "type": "LEGAL_INQUIRY",
        "entity_id": request.entity_id,
        "authority": request.legal_authority,
        "context": request.case_context,
        "status": "Generated"
    }
    FirestoreService.log_decision(packet)
    return {"status": "success", "packet_id": "inq_001"}

@app.get("/api/audit/logs")
def get_audit_logs():
    # Mock logs
    return [
        {"timestamp": "2025-10-27T10:00:00", "action": "LOGIN", "user": "analyst_01"},
        {"timestamp": "2025-10-27T10:15:00", "action": "VIEW_ENTITY", "entity": "c_102", "user": "analyst_01"},
        {"timestamp": "2025-10-27T11:00:00", "action": "SAR_DRAFT_CREATED", "entity": "c_145", "user": "analyst_01"}
    ]

# --- Informer & Analyst Endpoints ---

@app.post("/api/reports/submit")
async def submit_informer_report(request: InformerReportRequest):
    report_id = f"rpt_{len(informer_reports_db) + 100}"
    new_report = request.dict()
    new_report.update({
        "id": report_id,
        "status": "Submitted",
        "timestamp": datetime.now().isoformat(),
        "notes": []
    })
    informer_reports_db.append(new_report)
    FirestoreService.log_decision({"type": "INFORMER_SUBMISSION", "id": report_id})
    return {"status": "success", "report_id": report_id}

@app.get("/api/reports/list")
def get_all_reports(role: str = "analyst", reporter_id: str = None):
    if role == "informer":
        return [r for r in informer_reports_db if r['reporter_id'] == reporter_id]
    return informer_reports_db

@app.post("/api/reports/review")
async def review_report(request: ReportReviewRequest):
    report = next((r for r in informer_reports_db if r['id'] == request.report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report['status'] = "Closed" if request.action == "DISMISS" else "Under Investigation"
    if request.action == "CASE":
        report['status'] = "Converted to Case"
    
    # Generate AI Insight for the review
    ai_insight = await GeminiService.generate_text(f"Analyze this informer report action: {request.action}. Notes: {request.notes}")
    
    report['notes'].append({
        "analyst": request.analyst_id,
        "action": request.action,
        "note": request.notes,
        "ai_insight": ai_insight,
        "timestamp": datetime.now().isoformat()
    })
    
    FirestoreService.log_decision({"type": "REPORT_REVIEW", "id": request.report_id, "action": request.action})
    return {"status": "success", "ai_insight": ai_insight}
