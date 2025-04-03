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
You are a product review analysis assistant.
Find real, authentic user reviews from trustworthy online sources about the product with code or title: {key}.
Your task is to:
1. Summarize the most common feedback into **4 distinct sentences**.
2. Use a **natural and professional but human tone**, like genuine review summaries.
3. Do **not** repeat the product model or SKU in the text.
4. Begin the summary directly – no phrases like \"Users find\" or \"The product is...\"
5. Vary the wording and phrasing from product to product.
6. Return a **short, 3-4 word title** summarizing the sentiment or core idea.
7. Estimate the **number of total reviews**, try to be accurate (not rounded), based on what you find.
8. Return a valid JSON response like:
{{
  "average_score": float (from 0 to 5),
  "summary": "string of 4 sentences",
  "total_reviews": int,
  "title": "short summary title"
}}
{lang_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
