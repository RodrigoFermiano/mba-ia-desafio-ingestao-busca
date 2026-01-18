# Desafio MBA Engenharia de Software com IA - Full Cycle

Esta aplicação é um sistema de Recuperação de Informação Aumentada (RAG - Retrieval-Augmented Generation) que permite ingerir documentos PDF, armazená-los em um banco de dados vetorial e realizar buscas semânticas baseadas em perguntas do usuário.

## Funcionalidades

- **Ingestão de PDF**: Carrega um arquivo PDF, divide o conteúdo em chunks e cria embeddings usando OpenAI para armazenar em um banco PostgreSQL com extensão pgvector.
- **Busca Semântica**: Realiza buscas por similaridade no conteúdo ingerido, retornando trechos relevantes com pontuações.
- **Chat Simples**: Interface básica para fazer perguntas sobre o documento ingerido.

## Pré-requisitos

- **Python 3.8+**: Certifique-se de ter o Python instalado.
- **Docker e Docker Compose**: Para executar o banco de dados PostgreSQL com pgvector.
- **Chave da API OpenAI**: Você precisa de uma chave válida da OpenAI para gerar embeddings e (potencialmente) respostas.
- **Arquivo PDF**: Um documento PDF para ser ingerido (configure o caminho na variável de ambiente `PDF_PATH`).

## Instalação e Configuração

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd mba-ia-desafio-ingestao-busca
   ```

2. **Configure o ambiente virtual Python**:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   
   Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
   ```
   OPENAI_API_KEY=sua-chave-api-openai-aqui
   PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/rag
   PGVECTOR_COLLECTION=documentos
   PDF_PATH=../data/exemplo.pdf  # Caminho relativo ao arquivo PDF a ser ingerido
   EMBEDDING_MODEL=text-embedding-3-small  # Modelo de embedding (opcional)
   ```

   - Substitua `sua-chave-api-openai-aqui` pela sua chave da API OpenAI.
   - Ajuste `PDF_PATH` para o caminho do seu arquivo PDF (relativo à pasta `src/`).

5. **Inicie o banco de dados**:
   ```bash
   docker-compose up -d
   ```
   Isso iniciará um container PostgreSQL com a extensão pgvector.

## Como Executar

### 1. Ingerir o Documento PDF

Execute o script de ingestão para carregar o PDF no banco vetorial:
```bash
python src/ingest.py
```
Este comando irá:
- Carregar o PDF especificado em `PDF_PATH`.
- Dividir o conteúdo em chunks de 1000 caracteres com sobreposição de 150.
- Gerar embeddings usando OpenAI.
- Armazenar os vetores no PostgreSQL.

### 2. Realizar Buscas ou Chat

#### Busca Direta
Para realizar uma busca semântica, você pode modificar o arquivo `src/chat.py` para alterar a pergunta, ou executar diretamente o módulo de busca.

#### Chat Simples
Execute o chat para fazer uma pergunta pré-definida:
```bash
python src/chat.py
```
Este comando executará uma busca baseada na pergunta hardcoded no arquivo (sobre "Cobalto Energia Indústria"). Os resultados serão impressos no console.

Para perguntas personalizadas, edite a variável `question` em `src/chat.py` antes de executar.

## Estrutura do Projeto

```
.
├── docker-compose.yml      # Configuração do banco de dados
├── requirements.txt        # Dependências Python
├── src/
│   ├── ingest.py          # Script de ingestão de PDF
│   ├── search.py          # Função de busca semântica
│   └── chat.py            # Interface simples de chat
└── README.md              # Este arquivo
```

## Notas Técnicas

- O sistema usa LangChain para processamento de documentos e integração com OpenAI.
- O banco de dados vetorial permite buscas por similaridade coseno.
- A conectividade com o banco é testada automaticamente, ajustando hosts se necessário (útil em ambientes Docker no Windows).
- Certifique-se de que o arquivo PDF existe no caminho especificado antes de executar a ingestão.

## Solução de Problemas

- **Erro de conectividade com PostgreSQL**: Verifique se o Docker está rodando e o container está saudável (`docker-compose ps`).
- **Erro de API OpenAI**: Confirme se a chave da API está correta e tem créditos suficientes.
- **Arquivo PDF não encontrado**: Verifique o caminho em `PDF_PATH` e se o arquivo existe.
- **Dependências faltando**: Execute `pip install -r requirements.txt` novamente.

## Contribuição

Para contribuir, faça um fork do repositório, crie uma branch para suas mudanças e envie um pull request.