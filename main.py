from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# לאפשר CORS כדי לאפשר גישה מהדומיין של שופיפיי
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductRequest(BaseModel):
    title: str
    sku: str
    barcode: str

@app.post("/api/product-summary")
def get_summary(product: ProductRequest):
    return JSONResponse(
        content={
            "product_name": product.title,
            "average_score": 4.12,
            "sources": [
                {"site": "Amazon", "score": 4.3, "reviews": 1241, "estimated": False},
                {"site": "BestBuy", "score": 4.6, "reviews": 623, "estimated": False},
                {"site": "PCMag", "score": 3.0, "reviews": None, "estimated": False},
                {"site": "Reddit", "score": 4.5, "reviews": None, "estimated": True}
            ],
            "summary": "מחשב משתלם עם ביצועים חזקים לגיימינג, אך איכות הבנייה בינונית."
        },
        media_type="application/json; charset=utf-8"
    )
