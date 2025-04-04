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
async def get_summary(data: dict):
    key = data.get("sku")
    lang = data.get("lang", "he")

    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "כתוב בעברית בבקשה." if lang == "he" else "Please write in English."

    prompt = f"""
You are a professional product reviewer. Your task is to research and write a single third-person, natural-sounding product review, based on real user reviews from multiple sources (such as Amazon, Reddit, forums, tech sites, etc). Use aggregated insights and transform them into a fluent, human-sounding review.

⚠️ The review must:
- Be written in third-person only (no “users say”, “customers mention”, or “this product”).
- Read like a single opinionated review, not a summary.
- Contain exactly 4 informative sentences, including pros and cons.
- Vary wording between products.
- Be neutral, professional, and clear. No exaggerated marketing terms.
- Do not repeat the product model or brand in the text.

Use only real, reliable feedback. Return the result in this JSON format:

{{
  "average_score": float (e.g., 4.2),
  "summary": "4-sentence aggregated third-person review",
  "total_reviews": integer (not rounded),
  "title": "3–4 word opinion title"
}}

{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You analyze user reviews from the internet and summarize them."},
                {"role": "user", "content": prompt.replace("{key}", key)}
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        print("GPT raw output:", content)
        result = json.loads(content)
        return result

    except Exception as e:
        print(f"Error during GPT call:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
