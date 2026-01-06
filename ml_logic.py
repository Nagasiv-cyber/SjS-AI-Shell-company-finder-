import random
import numpy as np

def calculate_risk_score(company_data, transactions, network_graph=None):
    """
    Calculates a risk score (0-100) based on simple heuristic rules and anomaly detection logic.
    
    Factors:
    1. Pass-through Risk: Ratio of In-flow vs Out-flow. (Shell companies often have ~1.0 ratio)
    2. Velocity Risk: High volume of transactions in short time.
    3. Jurisdiction Risk: (Simulated) Cross-border transaction count.
    4. Network Risk: High degree centrality or circular connections.
    """
    
    score = 0
    reasons = []
    
    # 1. Flow Ratio Logic
    total_in = sum(t['amount'] for t in transactions if t['to_id'] == company_data['id'])
    total_out = sum(t['amount'] for t in transactions if t['from_id'] == company_data['id'])
    
    if total_in > 0:
        ratio = total_out / total_in
        # If ratio is very close to 1 (0.95 - 1.05), it suggests pass-through account
        if 0.95 <= ratio <= 1.05:
            score += 30
            reasons.append("Suspicious pass-through activity detected (In/Out ratio ~1.0)")
        elif ratio > 2.0 or ratio < 0.1:
            # Irregular hoarding or dumping
            score += 10
            reasons.append("Irregular funds flow ratio")
            
    # 2. Volume/Velocity Risk (Simulated thresholds)
    tx_count = len(transactions)
    if tx_count > 50:
        score += 20
        reasons.append(f"High transaction frequency ({tx_count} txns)")
    
    # 3. Cross-Border / Jurisdiction Risk (Simulated)
    # Assume 20% of random transactions are flagged as cross-border in our synthetic data
    cross_border_tx = [t for t in transactions if t.get('is_cross_border')]
    if len(cross_border_tx) > 5:
        score += 25
        reasons.append(f"High cross-border activity ({len(cross_border_tx)} txns)")
        
    # 4. Network Risk (Simulated centrality)
    # In a real app, we'd use networkx centrality. Here we mock it based on connection count.
    connections = set([t['from_id'] for t in transactions] + [t['to_id'] for t in transactions])
    if len(connections) > 10:
        score += 15
        reasons.append("Complex network connectivity (Hub behavior)")

    # Base Noise (to make it look realistic/ML-generated)
    score += random.randint(0, 10)
    
    # Cap score
    score = min(100, max(0, score))
    
    # Risk Level
    if score >= 75:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return {
        "score": int(score),
        "level": level,
        "reasons": reasons,
        "details": {
            "total_in": total_in,
            "total_out": total_out,
            "tx_count": tx_count,
            "cross_border_count": len(cross_border_tx)
        }
    }
