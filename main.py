import os
import json
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/api/product-summary")
async def get_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")

    key = sku or barcode
    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please respond in Hebrew." if lang == "he" else "Please respond in English."

    prompt = f"""
You are a product analyst AI. Find real user reviews from trusted online sources about the product with code: {key}.
Summarize the most common feedback in 2 sentences.
Respond only with valid JSON in this format:
{{
  "average_score": float,
  "summary": "string",
  "total_reviews": int
}}
{lang_instruction}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
