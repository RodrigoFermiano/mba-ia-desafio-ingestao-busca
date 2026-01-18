import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
import socket
from urllib.parse import urlparse


OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
PGVECTOR_URL=os.getenv("PGVECTOR_URL")
PGVECTOR_COLLECTION=os.getenv("PGVECTOR_COLLECTION")
PDF_PATH=os.getenv("PDF_PATH")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):

  for k in(OPENAI_API_KEY, PGVECTOR_URL, PGVECTOR_COLLECTION):
    if not k:
      raise RuntimeError(f"Variavel de ambiente não foi habilitada")


    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Testa conectividade e ajusta URL automaticamente se necessário
    pgvector_url = PGVECTOR_URL
    parsed_url = urlparse(pgvector_url)
    original_hostname = parsed_url.hostname or "localhost"
    port = parsed_url.port or 5432

    # Testa conectividade com diferentes hosts (host.docker.internal pode não funcionar no Windows)
    test_hosts = [original_hostname, "localhost", "127.0.0.1"]
    accessible_host = None

    for test_host in test_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            if sock.connect_ex((test_host, port)) == 0:
                accessible_host = test_host
                sock.close()
                break
            sock.close()
        except:
            continue

    # Se encontrou um host acessível diferente do original, ajusta a URL
    if accessible_host and accessible_host != original_hostname:
        parsed_url = urlparse(pgvector_url)
        if parsed_url.password:
            new_netloc = f"{parsed_url.username}:{parsed_url.password}@{accessible_host}:{port}"
        elif parsed_url.username:
            new_netloc = f"{parsed_url.username}@{accessible_host}:{port}"
        else:
            new_netloc = f"{accessible_host}:{port}"
        pgvector_url = f"{parsed_url.scheme}://{new_netloc}{parsed_url.path}"

    store = PGVector(
        embeddings=embeddings,
        collection_name=PGVECTOR_COLLECTION,
        connection=pgvector_url,
        use_jsonb=True,
       
    )

  results = store.similarity_search_with_score(PROMPT_TEMPLATE, k=10)

  for i, (doc, score) in enumerate(results, start=1):
      print("="*50)
      print(f"Resultado {i} (score: {score:.2f}):")
      print("="*50)

      print("\nTexto:\n")
      print(doc.page_content.strip())

      print("\nMetadados:\n")
      for k, v in doc.metadata.items():
          print(f"{k}: {v}")

