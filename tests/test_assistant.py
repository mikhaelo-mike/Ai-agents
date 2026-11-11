from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from company_assistant import api
from company_assistant.graph import build_graph


class FakeRetriever:
    def invoke(self, question: str) -> list[Document]:
        assert question == "How long does delivery take?"
        return [
            Document(
                page_content="Standard delivery takes 3 to 5 business days.",
                metadata={"source": "company_info.md"},
            )
        ]


def test_graph_retrieves_context_and_returns_answer() -> None:
    graph = build_graph(
        FakeRetriever(),
        FakeListChatModel(responses=["Standard delivery takes 3 to 5 business days."]),
    )

    result = graph.invoke({"question": "How long does delivery take?"})

    assert result["answer"] == "Standard delivery takes 3 to 5 business days."
    assert result["documents"][0].metadata["source"] == "company_info.md"


def test_ask_endpoint_returns_answer_and_source(monkeypatch) -> None:
    class FakeGraph:
        def invoke(self, state: dict[str, str]) -> dict:
            assert state["question"] == "How long does delivery take?"
            return {
                "answer": "3 to 5 business days.",
                "documents": [
                    Document(
                        page_content="Delivery takes 3 to 5 business days.",
                        metadata={"source": "company_info.md"},
                    )
                ],
            }

    monkeypatch.setattr(api, "get_answer_graph", lambda: FakeGraph())
    client = TestClient(api.app)

    response = client.post(
        "/ask", json={"question": "How long does delivery take?"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "3 to 5 business days.",
        "sources": ["company_info.md"],
    }


def test_health_endpoint() -> None:
    client = TestClient(api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
