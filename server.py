from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime, timezone
from collections import Counter

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

app = FastAPI()
api = APIRouter(prefix="/api")

# Codes d'accès -> pseudo (un par étudiant)
CODES = {
    "GRADI2026": "Alice",
    "BOB2026": "Bob",
    "CHLOE2026": "Chloé",
    "DAVID2026": "David",
    "EMMA2026": "Emma",
    "FARID2026": "Farid",
    "GASPARD2026": "Gaspard",
    "HUGO2026": "Hugo",
    "INES2026": "Inès",
    "JULES2026": "Jules",
}

ADMIN_CODE = "BONJOURADMIN2026"


class LoginIn(BaseModel):
    code: str


class MessageIn(BaseModel):
    code: str
    text: str


@api.post("/login")
async def login(payload: LoginIn):
    pseudo = CODES.get(payload.code.strip().upper())
    if not pseudo:
        raise HTTPException(status_code=401, detail="Code invalide")
    return {"pseudo": pseudo}


@api.get("/messages")
async def get_messages():
    msgs = await db.messages.find({}, {"_id": 0}).sort("ts", 1).to_list(500)
    return msgs


@api.post("/messages")
async def post_message(payload: MessageIn):
    pseudo = CODES.get(payload.code.strip().upper())
    if not pseudo:
        raise HTTPException(status_code=401, detail="Code invalide")
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message vide")
    if len(text) > 500:
        text = text[:500]
    doc = {
        "pseudo": pseudo,
        "text": text,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    await db.messages.insert_one(doc)
    return {"ok": True}


@api.get("/admin/stats")
async def admin_stats(code: str):
    if code.strip().upper() != ADMIN_CODE:
        raise HTTPException(status_code=401, detail="Code admin invalide")

    msgs = await db.messages.find({}, {"_id": 0}).sort("ts", 1).to_list(10000)
    total = len(msgs)
    by_user = Counter(m["pseudo"] for m in msgs)
    last_seen = {}
    for m in msgs:
        last_seen[m["pseudo"]] = m["ts"]
    by_hour = Counter()
    for m in msgs:
        try:
            h = datetime.fromisoformat(m["ts"]).hour
            by_hour[h] += 1
        except Exception:
            pass

    students = []
    for pseudo in sorted(set(CODES.values())):
        students.append({
            "pseudo": pseudo,
            "messages": by_user.get(pseudo, 0),
            "last_seen": last_seen.get(pseudo),
        })

    return {
        "total_messages": total,
        "total_students": len(set(CODES.values())),
        "active_students": sum(1 for s in students if s["messages"] > 0),
        "students": students,
        "by_hour": [{"hour": h, "count": by_hour.get(h, 0)} for h in range(24)],
        "last_messages": msgs[-10:][::-1],
    }


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    client.close()
