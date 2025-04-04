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
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")

    key = sku or barcode
    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please write in Hebrew." if lang == "he" else "Please write in English."

    prompt = f"""
Act as a professional product reviewer. Based on your knowledge and typical online user feedback, write a **realistic review** for the product with model code: {key}.

Your output must follow these rules:
1. **Write in the voice of a single reviewer**, as if it's a genuine, natural human review. For example: "The laptop is reliable and fast" — not "users appreciate...".
2. Use a **natural, professional, and human tone**, like a genuine review.
3. Write a **3–4 sentence paragraph**.
4. It should be **a product review**, not a general product description.
5. Avoid any marketing buzzwords or vague generalities.
6. Do **not** mention the product model or SKU in the text.
7. Vary the wording and phrasing between products.
8. Return a short **3–4 word title** that captures the core idea or sentiment (do not include product name).
9. Estimate the **exact number of reviews**, based on what you find (not rounded).
10. Keep the score and total reviews **consistent for the same product** over multiple runs.

Respond **only** with valid JSON in the following format — no explanation, no markdown, no extra text, and no apology:
{{
  "average_score": float (e.g. 4.3),
  "summary": "your 3–4 sentence review",
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

        content = response.choices[0].message.content.strip()
        print("GPT raw output:", content)

        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            print("Invalid JSON returned")
            return JSONResponse({"error": "Invalid JSON from GPT"}, status_code=500)

    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
