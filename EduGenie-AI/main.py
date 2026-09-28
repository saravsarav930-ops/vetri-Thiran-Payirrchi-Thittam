import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google import genai


# Load environment variables
load_dotenv()

# Get Gemini settings
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please add it to the .env file."
    )

# Create Gemini client
client = genai.Client(api_key=API_KEY)

# Create FastAPI application
app = FastAPI(title="EduGenie - AI Learning Assistant")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "question": "",
        "answer": None
    }
)


@app.post("/ask", response_class=HTMLResponse)
async def ask(
    request: Request,
    question: str = Form(...)
):
    question = question.strip()

    if not question:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "answer": "Please enter a question.",
                "question": ""
            }
        )

    try:
        prompt = f"""
You are EduGenie, a friendly AI learning assistant.

Help the student understand the following question clearly.

Rules:
- Use simple English.
- Explain step by step.
- Give examples when useful.
- For programming questions, give simple code.
- Do not make the answer unnecessarily complicated.

Student question:
{question}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text

    except Exception as error:
        answer = (
            "Sorry, something went wrong while contacting Gemini. "
            f"Error: {error}"
        )

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "question": question,
        "answer": answer
    }
)