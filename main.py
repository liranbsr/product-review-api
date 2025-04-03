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

    lang_instruction = "Please write in Hebrew." if lang == "he" else "Please write in English."

    prompt = f"""
Act as a product review analyst. Based on typical online user feedback, provide an authentic-looking summary for the product with model code: {key}.
Your task:

1. Summarize common feedback in **4 varied sentences**.
2. Use a **natural, professional, human tone** – like a real review.
3. **Don't** repeat the product model or SKU in the text.
4. Avoid phrases like "users say", "users find", or "users praise" – just describe the product directly.
5. Vary the style and phrasing between summaries.
6. Provide a **short, 3–4 word title** that captures the sentiment or main point.
7. Estimate the **number of total reviews** (as close and realistic as possible).
8. Respond in **valid JSON**, with this format:

{{
  "average_score": float from 0 to 5,
  "summary": "4 full review-style sentences",
  "total_reviews": int,
  "title": "3–4 word summary title"
}}

{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You analyze user reviews from the internet and summarize them."},
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
