from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph


class AssistantState(TypedDict, total=False):
    question: str
    documents: list[Document]
    answer: str


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using only the company information below. "
            "If it does not contain the answer, say you don't know. "
            "Keep the answer concise.\n\nCompany information:\n{context}",
        ),
        ("human", "{question}"),
    ]
)


def build_graph(retriever: Runnable, model: Runnable):
    def retrieve(state: AssistantState) -> AssistantState:
        return {"documents": retriever.invoke(state["question"])}

    def answer(state: AssistantState) -> AssistantState:
        context = "\n\n".join(
            document.page_content for document in state.get("documents", [])
        )
        response = (PROMPT | model).invoke(
            {"question": state["question"], "context": context}
        )
        return {"answer": str(response.content)}

    graph = StateGraph(AssistantState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("answer", answer)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)
    return graph.compile()
