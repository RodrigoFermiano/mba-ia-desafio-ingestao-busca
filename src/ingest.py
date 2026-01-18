import os
import socket
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
PGVECTOR_URL=os.getenv("PGVECTOR_URL")
PGVECTOR_COLLECTION=os.getenv("PGVECTOR_COLLECTION")
PDF_PATH=os.getenv("PDF_PATH")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def ingest_pdf():
    for k in(OPENAI_API_KEY, PGVECTOR_URL, PGVECTOR_COLLECTION):
        if not k:
            raise RuntimeError(f"Variavel de ambiente não foi habilitada")

    # usando caminho absoluto baseado no diretório do script para evitar problemas com CWD do windows
    script_dir = Path(__file__).parent.absolute()
    pdf_path = (script_dir / f"{PDF_PATH}").as_posix()

    docs = PyPDFLoader(pdf_path).load()

    splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, add_start_index=False).split_documents(docs)

    if not splits:
        raise SystemExit(0)

    enriched =[
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splits
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

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

    store.add_documents(documents=enriched,ids=ids)


if __name__ == "__main__":
    ingest_pdf()