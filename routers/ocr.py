import io
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from PIL import Image
import pytesseract

from schemas import OcrResult

router = APIRouter(
    prefix="/api/v1/ocr",
    tags=["OCR"]
)

@router.post(
    "/upload",
    response_model=OcrResult,
    status_code=status.HTTP_200_OK
)
async def ocr_image(
    file: UploadFile = File(..., description="Resim dosyası (png, jpg, jpeg)")
) -> OcrResult:
    """
    Kullanıcının yüklediği resim dosyasındaki metni OCR ile tanır ve döner.
    """
    # Dosya tipi kontrolü
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz dosya türü. Lütfen bir resim yükleyin."
        )
    try:
        # Dosya içeriğini oku
        contents = await file.read()
        # PIL ile resmi aç
        image = Image.open(io.BytesIO(contents))
        # OCR işlemi
        text = pytesseract.image_to_string(image)
        return OcrResult(text=text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR işlemi başarısız: {e}"
        )
    finally:
        await file.close()
