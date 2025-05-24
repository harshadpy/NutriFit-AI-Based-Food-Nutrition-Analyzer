from src.ai_model import get_nutrition_info, query_nutrition_knowledge
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "AI-based Food Nutrition Analyzer is running"}

@app.get("/analyze/{food_item}")
async def analyze_food(food_item: str):
    result = get_nutrition_info(food_item)
    response = {
        "food": food_item,
        "nutrition_info": result.replace("\n", " ")
    }
    return JSONResponse(content=response, status_code=200)

@app.get("/ask/{question}")
async def ask_question(question: str):
    result = query_nutrition_knowledge(question)
    response = {
        "question": question,
        "answer": result.replace("\n", " ")
    }
    return JSONResponse(content=response, status_code=200)