import json

from app.services.ollama import get_llm


INTENCOES_VALIDAS = {
    "criar_nota",
    "consultar_notas",
    "conversa_geral",
}


ROUTER_PROMPT = """
Classifique a intenção da mensagem do usuário.

Responda APENAS com um objeto JSON válido.
Não utilize markdown, comentários ou explicações adicionais.

Intenções possíveis:

1. criar_nota
Use quando o usuário pedir para criar, salvar, registrar,
adicionar ou anotar uma nota.

2. consultar_notas
Use quando o usuário perguntar sobre notas já criadas,
informações salvas, registros ou conteúdos anotados.

3. conversa_geral
Use quando a mensagem não depender das notas e não solicitar
a criação de uma nota.

Formato obrigatório:

{{
  "intencao": "criar_nota"
}}

O valor de "intencao" deve ser somente um destes:

- criar_nota
- consultar_notas
- conversa_geral

Mensagem do usuário:

{mensagem}
"""


def limpar_resposta_json(conteudo: str) -> str:
    conteudo = conteudo.strip()

    if conteudo.startswith("```json"):
        conteudo = conteudo.removeprefix("```json")
        conteudo = conteudo.removesuffix("```")
    elif conteudo.startswith("```"):
        conteudo = conteudo.removeprefix("```")
        conteudo = conteudo.removesuffix("```")

    return conteudo.strip()


async def classificar_intencao(mensagem: str) -> str:
    llm = get_llm()

    resposta = await llm.ainvoke(
        ROUTER_PROMPT.format(mensagem=mensagem)
    )

    conteudo = limpar_resposta_json(resposta.content)

    try:
        dados = json.loads(conteudo)
    except (json.JSONDecodeError, TypeError):
        return "consultar_notas"

    intencao = dados.get("intencao")

    if intencao not in INTENCOES_VALIDAS:
        return "consultar_notas"

    return intencao