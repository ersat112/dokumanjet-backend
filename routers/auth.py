from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"msg": "JWT login endpoint"}

@router.post("/register")
async def register():
    return {"msg": "User registered"}