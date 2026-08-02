from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ImageAnalysisRequest(BaseModel):
    image_url: str
    analysis_type: str = "classification"


class ImageAnalysisResponse(BaseModel):
    image_id: str
    analysis_type: str
    results: dict


@router.post("/analyze")
async def analyze_image(request: ImageAnalysisRequest):
    return {"message": "Image agent - analyze", "image_url": request.image_url}


@router.post("/classify")
async def classify_image():
    return {"message": "Image agent - classify"}


@router.post("/measure")
async def measure_phenotype():
    return {"message": "Image agent - measure phenotype"}


@router.post("/compare")
async def compare_images():
    return {"message": "Image agent - compare images"}
