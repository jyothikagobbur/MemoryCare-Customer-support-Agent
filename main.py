import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


# ============================================================
# MEMORYCARE APPLICATION
# ============================================================

app = FastAPI(title="MemoryCare")

templates = Jinja2Templates(directory="templates")

MEMORY_FILE = "memorycare_data.json"


# ============================================================
# LOCAL MEMORY FUNCTIONS
# ============================================================

def load_memories():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_memories(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memories, file, indent=4)


# ============================================================
# DATA MODELS
# ============================================================

class MemoryRequest(BaseModel):
    customer_id: str
    environment: str = ""
    issue: str
    solution: str


class ChatRequest(BaseModel):
    customer_id: str
    message: str


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# ============================================================
# TEST
# ============================================================

@app.get("/test")
async def test():

    return {
        "status": "success",
        "message": "MemoryCare backend is running!"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "online",
        "message": "MemoryCare is running",
        "memory_engine": "Local Memory"
    }


# ============================================================
# SAVE CUSTOMER MEMORY
# ============================================================

@app.post("/memory")
async def save_memory(data: MemoryRequest):

    customer_id = data.customer_id.strip()
    environment = data.environment.strip()
    issue = data.issue.strip()
    solution = data.solution.strip()

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if not issue:
        return {
            "success": False,
            "message": "Previous issue is required."
        }

    if not solution:
        return {
            "success": False,
            "message": "Successful solution is required."
        }

    memories = load_memories()

    if customer_id not in memories:
        memories[customer_id] = []

    memories[customer_id].append({
        "environment": environment,
        "issue": issue,
        "solution": solution
    })

    save_memories(memories)

    return {
        "success": True,
        "message": f"Memory stored successfully for {customer_id}."
    }


# ============================================================
# RECALL CUSTOMER MEMORY
# ============================================================

@app.post("/recall")
async def recall_memory(data: ChatRequest):

    customer_id = data.customer_id.strip()
    question = data.message.strip()

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if not question:
        return {
            "success": False,
            "message": "Search question is required."
        }

    memories = load_memories()

    customer_memories = memories.get(customer_id, [])

    results = []

    for memory in customer_memories:

        text = (
            memory.get("issue", "") + " " +
            memory.get("solution", "") + " " +
            memory.get("environment", "")
        ).lower()

        question_words = question.lower().split()

        if any(word in text for word in question_words):
            results.append(
                f"Issue: {memory.get('issue')}\n"
                f"Environment: {memory.get('environment')}\n"
                f"Solution: {memory.get('solution')}"
            )

    return {
        "success": True,
        "customer_id": customer_id,
        "memories": results
    }


# ============================================================
# MEMORYCARE SUPPORT CHAT
# ============================================================

@app.post("/chat")
async def memorycare_chat(data: ChatRequest):

    customer_id = data.customer_id.strip()
    question = data.message.strip()

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if not question:
        return {
            "success": False,
            "message": "Customer problem is required."
        }

    memories = load_memories()

    customer_memories = memories.get(customer_id, [])

    matched_memory = None

    question_words = question.lower().split()

    for memory in reversed(customer_memories):

        text = (
            memory.get("issue", "") + " " +
            memory.get("solution", "")
        ).lower()

        if any(word in text for word in question_words):
            matched_memory = memory
            break

    if matched_memory:

        answer = (
            "I found a previous similar issue in the customer's history.\n\n"
            f"Previous issue: {matched_memory['issue']}\n\n"
            f"Successful solution: {matched_memory['solution']}"
        )

    else:

        answer = (
            "No previous similar solution was found for this customer.\n\n"
            "Please try the standard troubleshooting steps or provide "
            "more details about the problem."
        )

    # Save conversation
    if customer_id not in memories:
        memories[customer_id] = []

    memories[customer_id].append({
        "environment": "",
        "issue": question,
        "solution": answer
    })

    save_memories(memories)

    return {
        "success": True,
        "answer": answer,
        "memories": [
            {
                "issue": m.get("issue"),
                "solution": m.get("solution")
            }
            for m in customer_memories
        ]
    }


# ============================================================
# CUSTOMER HISTORY
# ============================================================

@app.get("/history/{customer_id}")
async def customer_history(customer_id: str):

    customer_id = customer_id.strip()

    memories = load_memories()

    customer_memories = memories.get(customer_id, [])

    return {
        "success": True,
        "customer_id": customer_id,
        "count": len(customer_memories),
        "memories": customer_memories
    }


# ============================================================
# APPLICATION INFORMATION
# ============================================================

@app.get("/info")
async def info():

    return {
        "application": "MemoryCare",
        "description": "AI Customer Support with Long-Term Memory",
        "backend": "FastAPI",
        "memory_engine": "Local Memory",
        "website": "http://127.0.0.1:8000"
    }