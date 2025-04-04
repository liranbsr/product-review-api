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
Find real user reviews from trustworthy online sources about the product with model code: {key}.
Your task is:
1. Research real reviews from as many reputable sources as possible.
2. Write a concise summary of 3–4 sentences, based on your findings.
3. Use third person only. No phrases like "users say" or "customers report". Just describe the product directly.
4. No marketing fluff. No repetition.
5. Include a short 3–4 word title that captures the essence of the review.
6. Estimate the total number of reviews as accurately as possible.
7. Return only valid JSON, like this:

{{
  "average_score": float (e.g. 4.3),
  "summary": "your 3–4 sentence summary here",
  "total_reviews": integer,
  "title": "3–4 word summary title"
}}

{lang_instruction}
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
