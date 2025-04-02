from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai
import os
import json

app = FastAPI()

# אפשר CORS לגישה מ-Shopify בלבד
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "data.json"
openai.api_key = os.getenv("OPENAI_API_KEY")

# טען את המאגר הקיים אם יש
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
else:
    db = {}

@app.post("/api/product-summary")
async def get_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")

    if not sku and not barcode:
        return JSONResponse({"error": "Missing SKU or Barcode"}, status_code=400)

    key = barcode or sku
    if key in db:
        return db[key]

    prompt = open("gpt_product_prompt.txt", "r", encoding="utf-8").read()
    prompt = prompt.replace("{{sku}}", sku or "").replace("{{barcode}}", barcode or "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        result = json.loads(content)

        # שמור למאגר
        db[key] = result
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        return result

    except Exception as e:
        print("GPT ERROR:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
