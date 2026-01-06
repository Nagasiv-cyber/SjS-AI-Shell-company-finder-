# AI-Based Shell Company Risk Identification System

## Overview
This project is a Proof of Concept (PoC) web application that demonstrates how Artificial Intelligence and Machine Learning can be used to identify potential shell company networks, money laundering patterns, and terrorism financing risks.

**NOTE:** This system generates synthetic probability scores. It is not a live intelligence tool.

## Key Features
- **Dashboard**: High-level metrics on processed entities and risk levels.
- **Risk Scoring Engine**: ML-heuristic hybrid logic to detect flow-through accounts, velocity anomalies, and complex networks.
- **Network Analysis**: Visual exploration of transaction relationships.
- **Alert Management**: Workflow for analysts to review high-risk entities.

## Architecture
- **Frontend**: React, Vite, Tailwind CSS, Recharts, Framer Motion.
- **Backend**: Python FastAPI, NetworkX (Graph Analysis), Scikit-learn (placeholder for advanced ML).
- **Data**: Synthetic generator using `Faker`.

## Setup Instructions

### Prerequisites
- Node.js (v16+)
- Python (3.8+)

### 1. Backend Setup
Navigate to the backend directory:
```bash
cd backend
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run the server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```
Install dependencies:
```bash
npm install
```
Run the development server:
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

## Legal & Ethical Disclaimer
This software is for demonstration and educational purposes only. The "Risk Scores" are generated based on synthetic patterns and do not represent real-world entities or criminal guilt. Any resemblance to real persons or companies is purely coincidental.
