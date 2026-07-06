from fastapi import APIRouter

router = APIRouter(prefix="/ask", tags=["AI"])


@router.post("")
async def ask_ai(data: dict):
    prompt = data.get("prompt", "")

    return {
        "success": True,
        "reply": f"You said: {prompt}"
    }
    