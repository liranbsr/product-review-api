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
Act as a professional product review analyst. Based on your knowledge and typical online user feedback, write an **aggregated summary** for the product with model code: {key}.

Your output must follow these rules:
1. Summarize the most common feedback into **3–4 complete sentences**.
2. Use a **natural, professional, and human tone**, like a genuine review.
3. Write it as a **summary of user opinions**, not a generic product description.
4. **Avoid marketing phrases** or general statements.
5. **Do not** repeat the product model or SKU in the text.
6. **Vary phrasing** between products to ensure unique style for each.
7. Return a **short, 3–4 word title** that captures the overall sentiment or insight (no product name in title).
8. Estimate the **total number of reviews** (as accurate as possible, not rounded).
9. **Keep average score and total reviews consistent** when summarizing the same product in future calls.

Respond **only with valid JSON** in the following format — no explanation, no markdown, no extra text, and no apology:

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
