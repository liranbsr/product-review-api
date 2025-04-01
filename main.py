from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# לאפשר קריאות CORS מכל דומיין (עבור Shopify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/product-summary")
async def get_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")

    if sku == "AL2Z5EA" or barcode == "AL2Z5EA":
        return {
            "product_name": sku,
            "average_score": 4.12,
            "sources": [
                {"site": "Amazon", "score": 4.3, "reviews": 1241, "estimated": False},
                {"site": "BestBuy", "score": 4.6, "reviews": 623, "estimated": False},
                {"site": "PCMag", "score": 3.0, "reviews": None, "estimated": False},
                {"site": "Reddit", "score": 4.5, "reviews": None, "estimated": True},
            ],
            "summary": "מחשב משתלם עם ביצועים חזקים לגיימינג, אך איכות הבנייה בינונית."
        }

    return {
        "product_name": sku,
        "average_score": None,
        "sources": [],
        "summary": ""
    }
