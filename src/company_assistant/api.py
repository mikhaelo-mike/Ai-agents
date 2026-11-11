from functools import lru_cache

from fastapi import FastAPI, HTTPException
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from pydantic import BaseModel, Field

from company_assistant.config import get_gemini_api_key, get_gemini_model_name
from company_assistant.graph import build_graph
from company_assistant.knowledge import build_retriever


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


@lru_cache(maxsize=1)
def get_answer_graph():
    api_key = get_gemini_api_key()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key,
    )
    retriever = build_retriever(embeddings)
    model = ChatGoogleGenerativeAI(
        api_key=api_key,
        model=get_gemini_model_name(),
        temperature=0,
    )
    return build_graph(retriever, model)


app = FastAPI(title="Company Info Assistant")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest) -> AnswerResponse:
    try:
        graph = get_answer_graph()
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    result = graph.invoke({"question": request.question})
    sources = sorted(
        {
            document.metadata.get("source", "company knowledge")
            for document in result.get("documents", [])
        }
    )
    return AnswerResponse(answer=result["answer"], sources=sources)
