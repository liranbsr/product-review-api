import os
import json
from fastapi import FastAPI
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
    sku = data.get("sku")
    barcode = data.get("barcode")
    title = data.get("title")
    lang = data.get("lang", "he")

    key = sku or barcode or title
    if not key:
        return JSONResponse({"error": "Missing SKU, Barcode, or Title"}, status_code=400)

    lang_instruction = "Please respond in Hebrew." if lang == "he" else "Please respond in English."

    prompt = f"""
You are a product analyst AI. Find real user reviews from trusted online sources about the product with the following information:
Title: {title}
Code: {key}

Based on these reviews:
1. Write a short headline-style summary of the product in 1 sentence (like a review title).
2. Write a brief summary of the most common feedback in 2 sentences.
3. Estimate the average user rating (from 1 to 5).
4. Estimate the total number of reviews found.

Respond only in valid JSON format like this:
{{
  "title_line": "string",
  "summary": "string",
  "average_score": float,
  "total_reviews": int
}}
{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        print("GPT raw output:", content)
        result = json.loads(content)
        return result

    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
