from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def generate_mock_data(num_companies=50, num_transactions=200):
    companies = []
    transactions = []
    
    # Generate Companies
    for i in range(num_companies):
        # Generate Banking Footprint (Mock)
        bank_profile = {
            "account_count": random.randint(1, 5),
            "jurisdictions": random.sample([fake.country_code() for _ in range(10)], random.randint(1, 3)),
            "risk_flags": random.sample(
                ["High-Risk Corridor", "Structuring Suspicion", "Rapid Pass-Through", "Velocity Spike", "Shell Characteristics"], 
                random.randint(0, 2)
            ),
            "accounts": [
                {
                    "bank_name": f"{fake.word().capitalize()} Bank Intl",
                    "masked_id": f"****{random.randint(1000, 9999)}",
                    "jurisdiction": fake.country_code()
                } for _ in range(random.randint(1, 3))
            ]
        }
        
        company = {
            "id": f"c_{i+100}",
            "name": fake.company(),
            "country": fake.country(),
            "inc_date": fake.date_between(start_date='-5y', end_date='today').isoformat(),
            "type": random.choice(["LLC", "Ltd", "Inc", "Corp", "Shell?"]),
            "status": "Active",
            "lat": float(fake.latitude()),
            "lng": float(fake.longitude()),
            "banking_profile": bank_profile
        }
        companies.append(company)
        
    # Generate Transactions
    for i in range(num_transactions):
        c1 = random.choice(companies)
        c2 = random.choice(companies)
        while c1['id'] == c2['id']:
            c2 = random.choice(companies)
            
        is_cross_border = c1['country'] != c2['country']
        
        tx = {
            "id": f"tx_{i+1000}",
            "from_id": c1['id'],
            "to_id": c2['id'],
            "amount": round(random.uniform(5000, 500000), 2),
            "date": fake.date_between(start_date='-1y', end_date='today').isoformat(),
            "is_cross_border": is_cross_border,
            "type": random.choice(["Wire", "Transfer", "Invoice", "Loan"])
        }
        transactions.append(tx)
        
    # Generate Ownerships
    ownerships = []
    for i in range(int(num_companies * 0.6)):
        owner = random.choice(companies)
        subsidiary = random.choice(companies)
        while owner['id'] == subsidiary['id']:
            subsidiary = random.choice(companies)
        
        # Avoid duplicate pairs
        if any(o['owner_id'] == owner['id'] and o['subsidiary_id'] == subsidiary['id'] for o in ownerships):
            continue

        ownership = {
            "owner_id": owner['id'],
            "subsidiary_id": subsidiary['id'],
            "percentage": round(random.uniform(5.0, 100.0), 1),
            "date_acquired": fake.date_between(start_date='-3y', end_date='today').isoformat()
        }
        ownerships.append(ownership)
        
    return companies, transactions, ownerships
