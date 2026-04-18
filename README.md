# ArchMind — Intelligent Architectural Analysis Engine

## Sobre

ArchMind é uma API FastAPI que recebe diagramas de arquitetura (imagens/PDFs) e retorna um relatório técnico estruturado com identificação de componentes, riscos e recomendações.

O projeto segue Clean Architecture: a camada HTTP (`api/`) delega a um pipeline sequencial de domínio (`core/`) sem nenhuma lógica de negócio no controller.

---

## Estrutura do Projeto

```
archmind/
 ├── api/
 │    └── routes/
 │         └── upload.py       # Endpoint HTTP
 ├── core/
 │    ├── extraction/          # Etapa 1 — extração de elementos (OCR futuro)
 │    ├── structuring/         # Etapa 2 — normalização para modelo estruturado
 │    ├── analysis/            # Etapa 3 — detecção de problemas e recomendações
 │    └── reporting/           # Etapa 4 — montagem do relatório final
 ├── schemas/
 │    └── report_schema.py     # Contrato de saída Pydantic
 ├── infra/
 │    └── storage/             # Persistência de arquivos (stub)
 ├── main.py
 ├── requirements.txt
 └── README.md
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

### 3. Rodar o servidor

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

---

## Documentação Interativa (Swagger UI)

Com o servidor rodando, acesse:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

No Swagger UI: clique em **POST /api/v1/upload-diagram → Try it out**, selecione um arquivo e clique em **Execute**.

---

## Roadmap

- [x] MVP FastAPI com pipeline mockado
- [ ] Extração real via OCR (Tesseract / modelo de visão)
- [ ] Mapeamento JSON de componentes
- [ ] Motor de análise com LLM
- [ ] Suporte a PDF
- [ ] Armazenamento persistente
- [ ] UI
