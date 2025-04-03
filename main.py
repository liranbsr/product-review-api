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
    lang = data.get("lang", "he")

    key = sku or barcode
    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please respond in Hebrew." if lang == "he" else "Please respond in English."

    prompt = f"""
You are an AI that summarizes real user reviews about a product. 
Find real user feedback from trusted sources on the internet (such as Amazon, Reddit, review sites, etc.) for the product with the following code:
{key}

1. Summarize the key insights in 4 sentences.
   - Only include findings that are supported by multiple user reviews.
   - Avoid general marketing language.
   - The tone should be trustworthy, professional, yet human — as if written by an analyst summarizing consumer feedback.

2. Write a short headline (3–4 words) summarizing the overall impression.
   - Do not include the product name in the title.
   - The title should reflect the general sentiment and main points.

3. Return the result in **valid JSON only**, with no formatting or extra characters:
{{
  "title": "string",
  "summary": "string (4 sentences)",
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
        content = response.choices[0].message.content.strip()

        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()

        result = json.loads(content)
        return result

    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
