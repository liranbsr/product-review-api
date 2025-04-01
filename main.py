import json
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "products.json"
openai.api_key = os.getenv("OPENAI_API_KEY")

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
else:
    db = {}

@app.post("/api/product-summary")
async def get_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")
    key = barcode or sku

    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    if key in db:
        return db[key]

    lang_instruction = "Please respond in Hebrew." if lang == "he" else "Please respond in English."

    prompt = f"""
    You are a product analyst AI. Find real user reviews from trusted online sources about the product with model code: {key}.
    Summarize the most common feedback in 2 sentences.
    {lang_instruction}
    Respond only with valid JSON in this format:
    {{
      "average_score": float,
      "summary": "string",
      "total_reviews": int
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        result = json.loads(content)

        db[key] = result
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
