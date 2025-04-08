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
async def get_summary(request: Request):
    data = await request.json()
    key = data.get("sku") or data.get("barcode")
    lang = data.get("lang", "he")

    if not key:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    lang_instruction = "Please write in Hebrew." if lang == "he" else "Please write in English."

    prompt = f"""
Find *authentic user reviews* from trustworthy online sources about the product with model code: {key}.

Your task is to **research thoroughly** and write a 3-4 sentence **review-style summary** in third person, as if written by a real person who tested the product – but based on aggregated reviews.

Guidelines:
1. Search and cross-reference multiple reputable sources (Amazon, BestBuy, Reddit, etc.).
2. Always write about the product itself – not what “users say” about it.
3. Use **direct third-person language**, like "The screen offers sharp contrast and smooth motion", not "Users report that the screen is good".
4. Do **not** mention the product name or model inside the text.
5. Use a **neutral, confident, and precise** tone – like an expert tech journalist.
6. Avoid vague words like “great”, “nice”, or “impressive”. Be specific.
7. Vary the structure and vocabulary between summaries.
8. Include a **3-4 word title** that reflects the *main takeaway*.
9. Estimate the **exact total number of reviews** based on your findings.
10. Output only valid **JSON**, like this:

{{
  "average_score": float (e.g. 4.3),
  "summary": "your 3-4 sentence natural-sounding review here",
  "total_reviews": integer,
  "title": "3-4 word title"
}}

{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You analyze user reviews from the internet and summarize them."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        result = json.loads(content)
        return result

    except Exception as e:
        print("Error during GPT call:", str(e))
        return JSONResponse(content={"error": "GPT call failed"}, status_code=500)
