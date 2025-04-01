
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins (for testing and integration with Shopify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Source(BaseModel):
    site: str
    score: float
    reviews: Union[int, None] = None
    estimated: bool = False

class ReviewSummary(BaseModel):
    product_name: str
    average_score: float
    sources: List[Source]
    summary: str

@app.get("/api/product-summary", response_model=ReviewSummary)
def get_summary(q: str):
    return ReviewSummary(
        product_name=q,
        average_score=4.12,
        sources=[
            {"site": "Amazon", "score": 4.3, "reviews": 1241},
            {"site": "BestBuy", "score": 4.6, "reviews": 623},
            {"site": "PCMag", "score": 3.0},
            {"site": "Reddit", "score": 4.5, "estimated": True}
        ],
        summary="מחשב משתלם עם ביצועים חזקים לגיימינג אך חיי סוללה בינוניים ואיכות בנייה בינונית."
    )
