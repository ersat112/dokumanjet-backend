from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
async def ocr_image():
    return {"text": "OCR sonucu"}