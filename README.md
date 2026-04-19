# ArchMind — Intelligent Architectural Analysis Engine

## Sobre

ArchMind é uma API FastAPI que recebe diagramas de arquitetura (imagens/PDFs) e retorna um relatório técnico estruturado com identificação de componentes, relacionamentos, estilo arquitetural, riscos e recomendações.

O projeto segue Clean Architecture: a camada HTTP (`api/`) delega a um pipeline sequencial de domínio (`core/`) sem nenhuma lógica de negócio no controller.

---

## Estrutura do Projeto

```
archmind/
 ├── api/
 │    └── routes/
 │         ├── upload.py          # Endpoint principal de upload
 │         └── structuring.py     # Endpoint direto de estruturação (dev/teste)
 ├── core/
 │    ├── extraction/             # Etapa 1 — extração de elementos (mockada)
 │    ├── structuring/            # Etapa 2 — estruturação com LLM (IMPLEMENTADA)
 │    │    ├── structurer.py      # Orquestrador da etapa
 │    │    ├── component_recognizer.py
 │    │    ├── relationship_recognizer.py
 │    │    ├── architecture_recognizer.py
 │    │    ├── validator.py
 │    │    └── prompts.py
 │    ├── enrichment/             # Etapa 3 — enriquecimento de metadados (stub)
 │    ├── analysis/               # Etapa 4 — detecção de problemas (mockada)
 │    └── reporting/              # Etapa 5 — montagem do relatório final
 ├── schemas/
 │    ├── report_schema.py        # Contrato de saída Pydantic
 │    └── structuring_schema.py   # Schemas de entrada para estruturação
 ├── infra/
 │    ├── llm/
 │    │    ├── base.py            # Classe abstrata LLMClient
 │    │    └── claude_client.py   # Implementação com Anthropic SDK
 │    └── storage/
 │         └── file_storage.py   # Persistência local de arquivos (stub)
 ├── tests/
 │    └── test_structuring.py    # Suite de testes da etapa 2
 ├── playground/
 │    └── testellm01.py          # Script de testes rápidos com LLM
 ├── main.py
 ├── requirements.txt
 └── README.md
```

---

## Pipeline de Processamento

O sistema processa diagramas em 5 etapas sequenciais:

| Etapa | Módulo | Status | Descrição |
|-------|--------|--------|-----------|
| 1 | `extraction` | Mockada | Extrai blocos de texto e elementos visuais do arquivo |
| 2 | `structuring` | **Implementada** | Identifica componentes, relacionamentos e estilo arquitetural via LLM |
| 3 | `enrichment` | Stub | Padroniza metadados e resolve aliases de domínio |
| 4 | `analysis` | Mockada | Detecta problemas e gera recomendações |
| 5 | `reporting` | Implementada | Monta o relatório final no schema de saída |

---

## Etapa 2 — Structuring (Implementada)

A camada de estruturação usa Claude Haiku via Anthropic SDK para transformar elementos brutos do diagrama em dados estruturados. São três reconhecedores independentes:

### Component Recognizer

- Recebe blocos de texto extraídos do diagrama
- Classifica cada componente em: `frontend`, `service` ou `database`
- Ignora ações e tipos de comunicação — foca apenas em entidades
- Parsing de JSON com fallback para blocos markdown

### Relationship Recognizer

- Infere relacionamentos entre os componentes identificados
- Classifica o tipo: `http_request`, `database_query` ou `internal_call`
- Garante integridade referencial: só cria relacionamentos entre IDs válidos

### Architecture Recognizer

- Identifica o estilo arquitetural geral: `layered`, `microservices`, `monolith`, etc.
- Normaliza a resposta para lowercase
- Retorna `"unknown"` quando não é possível determinar

### Endpoint de teste direto

```
POST /api/v1/structuring
```

Permite enviar `text_blocks` e `visual_elements` diretamente para a camada de estruturação sem passar pelo upload de arquivo.

**Request**

```json
{
  "text_blocks": ["API Gateway", "Auth Service", "User DB"],
  "visual_elements": [
    { "from": "API Gateway", "to": "Auth Service" },
    { "from": "Auth Service", "to": "User DB" }
  ]
}
```

**Response**

```json
{
  "components": [
    { "id": "c1", "name": "API Gateway", "type": "service" },
    { "id": "c2", "name": "Auth Service", "type": "service" },
    { "id": "c3", "name": "User DB", "type": "database" }
  ],
  "relationships": [
    { "from": "c1", "to": "c2", "type": "http_request" },
    { "from": "c2", "to": "c3", "type": "database_query" }
  ],
  "architecture_style": "microservices"
}
```

---

## Setup e Execução

### 1. Criar e ativar ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variável de ambiente

```bash
# Windows
set LLM_API_KEY=sua_chave_anthropic

# macOS / Linux
export LLM_API_KEY=sua_chave_anthropic
```

### 4. Rodar o servidor

```bash
uvicorn main:app --reload
```

O servidor sobe em `http://127.0.0.1:8000`.

---

## API

### POST /api/v1/upload-diagram

Envia um diagrama de arquitetura e recebe um relatório de análise estruturado.

**Request** — `multipart/form-data`

| Campo | Tipo   | Descrição                        |
|-------|--------|----------------------------------|
| file  | binary | Imagem ou PDF da arquitetura     |

**Response** — `application/json`

```json
{
  "diagram_name": "example.png",
  "summary": "Fluxo identificado com 4 etapas principais",
  "issues": [
    "Possível ausência de validação no passo 2",
    "Alto acoplamento entre serviços"
  ],
  "recommendations": [
    "Aplicar separação de responsabilidades",
    "Adicionar camada de validação"
  ]
}
```

### POST /api/v1/structuring

Endpoint direto para testar a camada de estruturação (ver seção Etapa 2 acima).

---

## Documentação Interativa (Swagger UI)

Com o servidor rodando, acesse:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Infraestrutura LLM

- **Modelo**: `claude-haiku-4-5-20251001` (velocidade e custo otimizados)
- **SDK**: `anthropic==0.96.0`
- **Max tokens**: 1024 por chamada
- **Chave de API**: variável de ambiente `LLM_API_KEY`
- **Abstração**: `LLMClient` (base abstrata) + `ClaudeClient` (implementação concreta)

---

## Testes

```bash
pytest tests/
```

A suite `tests/test_structuring.py` cobre:

- Payloads válidos — resposta 200 com campos corretos
- Payloads inválidos — validação de erros 422
- Parsing de JSON — com markdown, JSON limpo e entradas inválidas
- Integridade referencial de relacionamentos
- Normalização do estilo arquitetural

---

## Roadmap

- [x] MVP FastAPI com pipeline mockado
- [x] Infraestrutura LLM (Anthropic SDK + abstração)
- [x] Etapa 2 — Reconhecimento de componentes via LLM
- [x] Etapa 2 — Reconhecimento de relacionamentos via LLM
- [x] Etapa 2 — Identificação do estilo arquitetural via LLM
- [x] Etapa 2 — Validação de entrada com schema Pydantic
- [x] Etapa 2 — Endpoint direto `/api/v1/structuring`
- [x] Etapa 3 — Camada de enriquecimento (stub)
- [ ] Etapa 1 — Extração real via OCR (Tesseract / modelo de visão)
- [ ] Etapa 3 — Enriquecimento real com taxonomia de domínio
- [ ] Etapa 4 — Motor de análise com LLM
- [ ] Suporte a PDF
- [ ] Armazenamento persistente (S3/GCS)
- [ ] Etapa 5 — Geração do relatório final
- [ ] Protocolo de entrada de arquivo
- [ ] Protocolo de saída do relatório final
- [ ] Testar outros modelos, inclusive modelo aberto
