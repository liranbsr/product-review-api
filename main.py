import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/product-summary")
async def get_summary(request: Request):
    data = await request.json()
    key = data.get("sku") or data.get("barcode")
    lang = data.get("lang", "he")

    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please write in Hebrew." if lang == "he" else "Please write in English."

prompt = f"""
Find authentic user reviews from trustworthy online sources about the product with model code: {key}.
Your task is to research thoroughly and generate a natural and informative product review, as if it were written by a real person.

Guidelines:
1. Search multiple reputable sources (Amazon, BestBuy, Reddit, etc.) to collect real reviews.
2. Write a **concise, third-person product review** — exactly 3 to 4 sentences.
3. Do **not** mention users, customers, reviews, or the product model/code. Do **not** say “users report”, “people like”, “customers say”, etc.
4. Focus on the product itself: describe its screen, battery, design, materials, performance, or any common flaws.
5. Avoid marketing language, vague praise, or general statements.
6. Vary wording and phrasing — avoid repeating structures between products.
7. Include a **short, 3–4 word title** that reflects the product's character (e.g. "Solid Build, Average Battery").
8. Estimate the **exact number** of real reviews you found (not rounded).
9. Output must be in clean JSON **only** — no intro, no markdown, no explanation.

Format:
{{
  "average_score": float (e.g. 4.3),
  "summary": "3–4 sentence natural review here",
  "total_reviews": integer,
  "title": "3–4 word title"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse({"error": "GPT call failed"}, status_code=500)
