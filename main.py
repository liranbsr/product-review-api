import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/product-summary")
async def get_product_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")

    key = sku or barcode
    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please write in Hebrew." if lang == "he" else "Please write in English."

    prompt = f"""
Search for real, authentic user reviews from trustworthy online sources about the product with model code: {key}. Your goal is to write a single **aggregated review**, as if describing the product based on real user feedback — not as a summary of reviews and not as a first-person experience.

Do not mention the brand or model code within the review. Do not use phrases like “users say”, “many reviewers”, “customers report”, or “this product”. Just describe the product itself based on the web reviews aggregated info.

Your review must:
1. Be based on real user reviews from multiple sources (e.g., Amazon, Reddit, review sites).
2. Be written in a **natural, professional, and human tone**, like a product expert writing a review summary.
3. Avoid any marketing fluff or generic praise.
4. Be **exactly 4 full sentences**, including both pros and cons.
5. Be unique in style per product.
6. Do not invent data. Be realistic.
7. Return the result in the following valid JSON structure:
Respond **only** with valid JSON in the following format – no explanation, no markdown, no extra text, and no apology:
{{
  "average_score": float (from 0 to 5),
  "summary": "your 3–4 sentence aggregated review",
  "total_reviews": integer,
  "title": "3–4 word summary title"
}}
{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You analyze user reviews from the internet and summarize them."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        print("GPT raw output:", content)

        result = json.loads(content)
        return result

    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
