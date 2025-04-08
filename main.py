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
Find **authentic user reviews** from trustworthy online sources about the product with model code: {key}.

Your task is to **research thoroughly** and write a concise, realistic 3–4 sentence **review-style summary** in third person, as if written by a real person who tested the product – but based on **aggregated reviews**.

Guidelines:
1. Search and cross-reference multiple reputable sources (e.g. Amazon, BestBuy, Reddit, ZAP, forums) in **any relevant language** – including English, Hebrew, or others if available.
2. Only include reviews that refer specifically to the **exact model** code {key}. Do **not** include similar or related models. If no reliable reviews are found, return an error or fallback message.
3. Use a **natural, specific, and human tone**, like a real tech reviewer.
4. Avoid generic statements like “users appreciate” or “people say”. Just describe the product directly.
   ✅ Example: "The screen offers excellent brightness and color accuracy."
   ❌ Not: "Users say the screen is good."
5. Do **not** include the model number in the text.
6. Focus on actual performance: display, speed, battery, flaws, materials, real-world usage.
7. Vary structure and language between products. Avoid repetition.
8. Include a **short 3–4 word title** summarizing the main takeaway.
9. Estimate the **exact number of real reviews** found (not rounded).
10. Output must be clean JSON **only** — no intro, no explanation, no markdown.

Format:
{{
  "average_score": float (e.g. 4.3),
  "summary": "your 3–4 sentence natural-sounding review here",
  "total_reviews": integer,
  "title": "3–4 word title"
}}
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
