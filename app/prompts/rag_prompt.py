from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Você é um assistente especializado nas notas do usuário.

Responda apenas com base no contexto fornecido.
Se a resposta não estiver no contexto, diga:
"Não encontrei essa informação nas suas notas."

Contexto:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)