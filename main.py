import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# הגדרת המפתח שלך עבור OpenAI
openai.api_key = "הכנס את המפתח שלך כאן"

# הוספת CORS (Cross-Origin Resource Sharing) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # אפשר גישה מכל מקור
    allow_credentials=True,
    allow_methods=["*"],  # אפשר כל סוג של מתודה
    allow_headers=["*"],  # אפשר כל כותרת
)

@app.post("/api/product-summary")
async def get_summary(data: dict):
    sku = data.get("sku")
    barcode = data.get("barcode")
    lang = data.get("lang", "he")

    if not sku or not barcode:
        return JSONResponse(
            content={"error": "Missing SKU or Barcode"},
            status_code=400,
        )

    try:
        prompt = f"Product Name: {sku}. Find real user reviews from trusted online sources about the product with barcode {barcode}. Summarize the most common feedback in 1 sentence. Language: {lang}."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # שימוש במודל האחרון של GPT
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        return {"summary": result}

    except Exception as e:
        return JSONResponse(
            content={"error": f"Error in generating summary: {str(e)}"},
            status_code=500,
        )
