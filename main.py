from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY не найден в переменных окружения")

genai.configure(api_key=api_key)
system_instruction_text = "Отвечай кратко и только по существу запроса. Не добавляй лишних пояснений или вводных фраз, если это не требуется для ответа на сам вопрос. А также не используй маркировку (Markdown)"
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=system_instruction_text
)

app = FastAPI(title="Gemini Clipboard Helper API") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class AnswerResponse(BaseModel):
    answer: str


@app.post("/get_answer", response_model=AnswerResponse)
async def get_answer(request: PromptRequest):
    try:
        prompt_text = request.prompt
        
        if not prompt_text or prompt_text.strip() == "":
            raise HTTPException(status_code=400, detail="Prompt не может быть пустым")
        
        response = model.generate_content(prompt_text)
        
        answer_text = response.text
        
        return {"answer": answer_text}
    
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    certs_dir = os.path.join(script_dir, "certs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=443,
        reload=True,
        ssl_keyfile=os.path.join(certs_dir, "private.key"),
        ssl_certfile=os.path.join(certs_dir, "server.crt"),
        ssl_ca_certs=os.path.join(certs_dir, "root.crt")
    )