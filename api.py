"""
API factice (dummy) pour la Gate 1 - Hackathon Givaudan
Le Swagger est généré automatiquement : http://localhost:8000/docs
Lancer :  pip install fastapi uvicorn
          uvicorn api:app --port 8000
Puis dans un 2e terminal :  ngrok http 8000
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Tendances Givaudan",
              description="Brique Data : détecte les ingrédients en tendance émergente",
              version="0.1-dummy")

class Requete(BaseModel):
    termes: list[str] = ["Yuzu", "Matcha", "Vanilla"]

class Tendance(BaseModel):
    terme: str
    croissance_pct: float
    statut: str  # "émergent", "stable" ou "en baisse"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tendances", response_model=list[Tendance])
def tendances(req: Requete):
    # Réponse FACTICE : même format que le vrai modèle (V2 jeudi)
    return [Tendance(terme=t, croissance_pct=25.0, statut="émergent") for t in req.termes]
