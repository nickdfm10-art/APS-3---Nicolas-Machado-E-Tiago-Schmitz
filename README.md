# API de Eventos Acadêmicos — APS 3 (Persistência e Consolidação de Dados)

Equipe: Nicolas Machado e Tiago Schmitz

## 1. Descrição do projeto

API RESTful para gerenciar **eventos acadêmicos** (palestras, workshops, minicursos, seminários e competições), seus **participantes** e as **inscrições** dos participantes nos eventos.

Esta versão evolui a API da APS 2: os dados deixaram de ficar em listas na memória e agora são **persistidos em um banco SQLite** por meio do **SQLAlchemy ORM**. Além do CRUD, a API oferece **relatórios consolidados** (ocupação dos eventos, eventos por categoria e participação por curso), calculados dinamicamente com consultas SQLAlchemy (outer join, group by, count e sum).

Tecnologias: Python 3.10+, FastAPI, SQLAlchemy 2.x, SQLite, Pydantic v2, Uvicorn.

## 2. Instalação

```bash
# 1) clonar o repositório e entrar na pasta
git clone <url-do-repositorio>
cd aps3_eventos

# 2) criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate            # Windows (PowerShell: .\venv\Scripts\Activate)
source venv/bin/activate         # Linux / macOS

# 3) instalar as dependências
pip install -r requirements.txt
```

## 3. Execução

```bash
uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger (documentação e testes): http://127.0.0.1:8000/docs

As tabelas são criadas automaticamente na primeira execução. Para popular o banco com dados de exemplo (útil para testar os relatórios):

```bash
python seed.py
```

## 4. Estrutura do projeto

```
aps3_eventos/
├── main.py                  # cria a app, registra routers e tratadores de erro
├── database.py              # conexão SQLite, sessões (get_db) e criação das tabelas
├── exceptions.py            # exceções de negócio (404 / 409)
├── seed.py                  # dados de exemplo
├── controller/              # ROTAS HTTP (recebem a requisição e chamam o service)
│   ├── evento_controller.py
│   ├── participante_controller.py
│   ├── inscricao_controller.py
│   └── relatorio_controller.py
├── model/                   # ENTIDADES e relacionamentos (SQLAlchemy)
│   ├── evento.py
│   ├── participante.py
│   └── inscricao.py
├── schema/                  # VALIDAÇÃO de entrada e formato das respostas (Pydantic)
│   ├── evento_schema.py
│   ├── participante_schema.py
│   ├── inscricao_schema.py
│   ├── relatorio_schema.py
│   └── erro_schema.py
├── service/                 # REGRAS DE NEGÓCIO, persistência e consultas de consolidação
│   ├── evento_service.py
│   ├── participante_service.py
│   ├── inscricao_service.py
│   ├── relatorio_service.py
│   └── persistencia.py      # commit com tratamento de erros de integridade
├── tests/                   # testes automatizados (pytest)
├── requirements.txt         # dependências de execução
├── requirements-dev.txt     # + pytest e httpx (para os testes)
├── TESTES.md                # roteiro de testes no Swagger
└── README.md
```

| Camada | Responsabilidade |
|---|---|
| Controller | Rotas e recebimento das requisições HTTP. Sem regra de negócio. |
| Model | Tabelas e relacionamentos (SQLAlchemy). |
| Schema | Validação dos dados de entrada e definição das respostas (Pydantic). |
| Service | Regras de negócio, persistência e relatórios. |
| Database | Conexão, sessões e criação das tabelas. |

## 5. Configuração do banco de dados

- Banco: **SQLite**. O arquivo **`eventos.db`** é criado automaticamente **na raiz do projeto** (mesma pasta do `main.py`) e não é versionado (`.gitignore`).
- Para usar outro local, defina a variável de ambiente `EVENTOS_DATABASE_URL`, por exemplo: `sqlite:///C:/dados/eventos.db`.
- `database.py` configura o *engine*, a fábrica de sessões (`SessionLocal`), a dependência `get_db()` (abre uma sessão por requisição e **sempre a fecha** no final) e `criar_tabelas()` (chamada ao iniciar a aplicação).
- As chaves estrangeiras são ativadas em toda conexão (`PRAGMA foreign_keys=ON`), pois o SQLite as ignora por padrão.
- Para **zerar o banco**, pare a aplicação e apague o arquivo `eventos.db`.

### Modelo de dados

| Tabela | Colunas principais | Regras no banco |
|---|---|---|
| `eventos` | id, titulo, descricao, data, horario, local, capacidade, categoria | `capacidade > 0` (CHECK) |
| `participantes` | id, nome, email, curso | `email` **UNIQUE** |
| `inscricoes` | id, evento_id, participante_id, data_inscricao | FKs para `eventos` e `participantes` (ON DELETE RESTRICT) e **UNIQUE(evento_id, participante_id)** |

Relacionamentos: `Evento 1 ─── N Inscricao N ─── 1 Participante` (`Evento.inscricoes`, `Participante.inscricoes`, `Inscricao.evento`, `Inscricao.participante`).

## 6. Principais rotas

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| POST | `/eventos` | Cadastrar evento | 201 |
| GET | `/eventos` | Listar eventos | 200 |
| GET | `/eventos/{id}` | Consultar evento | 200 |
| PUT | `/eventos/{id}` | Atualizar evento | 200 |
| DELETE | `/eventos/{id}` | Excluir evento | 204 |
| POST | `/participantes` | Cadastrar participante | 201 |
| GET | `/participantes` | Listar participantes | 200 |
| GET | `/participantes/{id}` | Consultar participante | 200 |
| PUT | `/participantes/{id}` | Atualizar participante | 200 |
| DELETE | `/participantes/{id}` | Excluir participante | 204 |
| POST | `/eventos/{evento_id}/inscricoes/{participante_id}` | Inscrever participante | 201 |
| GET | `/eventos/{evento_id}/inscricoes` | Listar participantes inscritos no evento | 200 |
| DELETE | `/eventos/{evento_id}/inscricoes/{participante_id}` | Cancelar inscrição | 204 |
| GET | `/relatorios/eventos/ocupacao` | Relatório de ocupação | 200 |
| GET | `/relatorios/eventos/categorias` | Relatório por categoria | 200 |
| GET | `/relatorios/participantes/cursos` | Relatório por curso | 200 |

> O `id` é gerado pelo banco; **não deve ser enviado** no corpo das requisições.

## 7. Validações, erros e integridade

**Validações (Pydantic → HTTP 422):** título, descrição, local e nome não podem ser vazios (nem só espaços); e-mail com formato válido; capacidade maior que zero; data e horário válidos; categoria dentro da lista (Palestra, Workshop, Minicurso, Seminário, Competição); campos obrigatórios.

**Erros de negócio:**

| Situação | HTTP | `detail` |
|---|---|---|
| Evento inexistente | 404 | `Evento não encontrado.` |
| Participante inexistente | 404 | `Participante não encontrado.` |
| Inscrição inexistente (cancelamento) | 404 | `Inscrição não encontrada.` |
| Participante já inscrito | 409 | `Participante já está inscrito neste evento.` |
| Evento sem vagas | 409 | `Não existem vagas disponíveis para este evento.` |
| E-mail já cadastrado | 409 | `Já existe um participante cadastrado com este e-mail.` |
| Excluir evento com inscrições | 409 | `Não é possível excluir o evento, pois existem participantes inscritos. Cancele as inscrições antes.` |
| Excluir participante com inscrições | 409 | `Não é possível excluir o participante, pois ele possui inscrições. Cancele as inscrições antes.` |
| Reduzir capacidade abaixo dos inscritos | 409 | `A capacidade não pode ser menor que o número de inscritos (N).` |
| Falha inesperada no banco | 500 | `Erro ao acessar o banco de dados. Tente novamente mais tarde.` |

**Comportamento de exclusão (evita registros órfãos):** evento ou participante **com inscrições não pode ser excluído** (409). Para excluí-lo, primeiro cancele as inscrições (`DELETE /eventos/{evento_id}/inscricoes/{participante_id}`). A regra é aplicada no service e reforçada no banco (FK `ON DELETE RESTRICT`).

**Erros do banco:** violações de integridade (UNIQUE/FK) são capturadas, a transação sofre *rollback* e o cliente recebe uma mensagem amigável; detalhes técnicos vão apenas para o log do servidor.

**Ordem das verificações na inscrição:** evento existe → participante existe → já inscrito → há vagas. A duplicidade também é garantida pela constraint `UNIQUE(evento_id, participante_id)`.

## 8. Relatórios (consolidação de dados)

Todos retornam JSON, são calculados a cada requisição a partir do SQLite e devolvem `[]` quando não há registros.

### 8.1 `GET /relatorios/eventos/ocupacao`
Para cada evento: id, título, capacidade, total de inscritos, vagas disponíveis e percentual de ocupação (`inscritos / capacidade * 100`, 2 casas). Usa **outer join**, então eventos sem inscrições aparecem com 0; há proteção contra divisão por zero.

```json
[
  {"evento_id": 1, "titulo": "Introdução à Inteligência Artificial", "capacidade": 100,
   "total_inscritos": 6, "vagas_disponiveis": 94, "percentual_ocupacao": 6.0},
  {"evento_id": 2, "titulo": "Workshop de Python", "capacidade": 3,
   "total_inscritos": 3, "vagas_disponiveis": 0, "percentual_ocupacao": 100.0}
]
```

### 8.2 `GET /relatorios/eventos/categorias`
Por categoria: quantidade de eventos, capacidade total e total de inscrições. As inscrições são agrupadas por evento numa **subconsulta** antes de ligar aos eventos; assim a capacidade de um evento não é somada várias vezes (um JOIN direto inflaria os totais).

```json
[
  {"categoria": "Palestra", "total_eventos": 1, "capacidade_total": 100, "total_inscricoes": 6},
  {"categoria": "Workshop", "total_eventos": 2, "capacidade_total": 8, "total_inscricoes": 6}
]
```

### 8.3 `GET /relatorios/participantes/cursos`
Por curso: participantes cadastrados e total de inscrições. Mesma técnica de subconsulta: cada participante é contado **uma única vez**, mesmo com várias inscrições.

```json
[
  {"curso": "Engenharia de Software", "total_participantes": 3, "total_inscricoes": 9}
]
```

## 9. Exemplos de utilização

**Cadastrar evento** — `POST /eventos`
```json
{
  "titulo": "Workshop de FastAPI",
  "descricao": "Aprenda a criar APIs modernas",
  "data": "2026-12-10",
  "horario": "14:00",
  "local": "Laboratório 3",
  "capacidade": 2,
  "categoria": "Workshop"
}
```
Resposta `201`:
```json
{"id": 1, "titulo": "Workshop de FastAPI", "descricao": "Aprenda a criar APIs modernas",
 "data": "2026-12-10", "horario": "14:00:00", "local": "Laboratório 3",
 "capacidade": 2, "categoria": "Workshop"}
```

**Cadastrar participante** — `POST /participantes`
```json
{"nome": "Maria Souza", "email": "maria@email.com", "curso": "Engenharia de Software"}
```

**Inscrever** — `POST /eventos/1/inscricoes/1` → `201`
```json
{"id": 1, "evento_id": 1, "participante_id": 1, "data_inscricao": "2026-11-16"}
```

**Inscritos no evento** — `GET /eventos/1/inscricoes` → `200`
```json
[{"inscricao_id": 1, "data_inscricao": "2026-11-16",
  "participante": {"id": 1, "nome": "Maria Souza", "email": "maria@email.com",
                   "curso": "Engenharia de Software"}}]
```

**Erro** — repetir a inscrição → `409`
```json
{"detail": "Participante já está inscrito neste evento."}
```

Com `curl`:
```bash
curl -X POST http://127.0.0.1:8000/participantes \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria Souza","email":"maria@email.com","curso":"Engenharia de Software"}'
curl -X POST http://127.0.0.1:8000/eventos/1/inscricoes/1
curl http://127.0.0.1:8000/relatorios/eventos/ocupacao
```

## 10. Como reproduzir os testes

**a) Automatizados (pytest)** — usam um banco temporário, sem tocar no `eventos.db`:
```bash
pip install -r requirements-dev.txt
pytest -v
```
Cobrem CRUD, validações, inscrições (sucesso, duplicada, evento inexistente, sem vagas), integridade, persistência após reinício e os três relatórios (inclusive após inserir, atualizar e excluir).

**b) Manuais no Swagger** — siga o roteiro completo (12 cenários do enunciado) em [`TESTES.md`](TESTES.md).

## 11. Evolução em relação à APS 2

| APS 2 | APS 3 |
|---|---|
| Listas em memória (dados perdidos ao reiniciar) | SQLite + SQLAlchemy ORM (dados persistentes) |
| Rotas com lógica e armazenamento misturados | MVC: `controller` / `service` / `model` / `schema` / `database` |
| `id` enviado pelo cliente | `id` gerado pelo banco |
| `POST /inscricoes` com lista de participantes | `POST /eventos/{evento_id}/inscricoes/{participante_id}` |
| Sem `GET /eventos/{id}`, `GET /participantes/{id}` e `GET /eventos/{id}/inscricoes` | Rotas implementadas |
| Título/nome vazios, e-mail inválido e capacidade ≤ 0 aceitos; data como texto | Validação Pydantic (`EmailStr`, `gt=0`, `date`, `time`, textos não vazios) |
| Curso restrito a um enum com 3 valores | Curso livre (necessário ao relatório por curso) |
| Duplicidade/sem vagas com 400 | 409 Conflict |
| E-mail repetido permitido | E-mail único (código e constraint do banco) |
| Exclusão deixava inscrições órfãs | Exclusão bloqueada (409) enquanto houver inscrições |
| — | 3 relatórios consolidados + testes automatizados |
