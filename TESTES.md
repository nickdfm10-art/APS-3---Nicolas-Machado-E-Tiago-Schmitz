# Roteiro de testes — Swagger (`/docs`)

Comece com um banco limpo (apague `eventos.db` com a aplicação parada) e rode `uvicorn main:app --reload`.
Abra http://127.0.0.1:8000/docs, use **Try it out** em cada rota e tire *prints* da requisição e da resposta como evidência.

> Os cenários 1 a 8 e 12 usam dados criados à mão. Para os relatórios (9 a 11) pode-se usar o `python seed.py` (ver seção final).

## Preparação (dados base)

**P1.** `POST /eventos`
```json
{"titulo":"Workshop de FastAPI","descricao":"Aprenda a criar APIs modernas","data":"2026-12-10","horario":"14:00","local":"Laboratório 3","capacidade":2,"categoria":"Workshop"}
```
→ `201`, `"id": 1`

**P2.** `POST /participantes` → `201`, `"id": 1`
```json
{"nome":"Maria Souza","email":"maria@email.com","curso":"Engenharia de Software"}
```

**P3.** `POST /participantes` → `201`, `"id": 2`
```json
{"nome":"João Lima","email":"joao@email.com","curso":"Análise e Desenvolvimento de Sistemas"}
```

**P4.** `POST /participantes` → `201`, `"id": 3`
```json
{"nome":"Ana Costa","email":"ana@email.com","curso":"Engenharia de Software"}
```

## Cenários do enunciado

| # | Cenário | Requisição | Resultado esperado |
|---|---|---|---|
| 1 | Cadastro e consulta de eventos | `GET /eventos` e `GET /eventos/1` | `200` com o evento criado em P1 |
| 2 | Cadastro e consulta de participantes | `GET /participantes` e `GET /participantes/1` | `200` com os participantes |
| 3a | Atualização | `PUT /eventos/1` com `capacidade: 5` (demais campos iguais) | `200` com capacidade 5 |
| 3b | Exclusão | `POST /eventos` (novo evento, id 2) e depois `DELETE /eventos/2` | `204`; `GET /eventos/2` → `404` `{"detail":"Evento não encontrado."}` |
| 4 | Inscrição | `POST /eventos/1/inscricoes/1` | `201` com `evento_id:1`, `participante_id:1`, `data_inscricao` |
| 4b | Inscritos do evento | `GET /eventos/1/inscricoes` | `200` com Maria Souza na lista |
| 5 | Inscrição duplicada | `POST /eventos/1/inscricoes/1` (de novo) | `409` `{"detail":"Participante já está inscrito neste evento."}` |
| 6 | Evento inexistente | `POST /eventos/999/inscricoes/1` | `404` `{"detail":"Evento não encontrado."}` |
| 6b | Participante inexistente | `POST /eventos/1/inscricoes/999` | `404` `{"detail":"Participante não encontrado."}` |
| 7 | Sem vagas | Reduza a capacidade do evento 1 para 2 (`PUT`), inscreva o participante 2 (`201`) e depois o 3 | `409` `{"detail":"Não existem vagas disponíveis para este evento."}` |
| 8 | Persistência | Pare o servidor (Ctrl+C), suba de novo (`uvicorn main:app --reload`) e repita `GET /eventos`, `GET /participantes`, `GET /eventos/1/inscricoes` | Mesmos dados de antes do reinício |

### Cenários extras (validação e integridade)

| Teste | Requisição | Esperado |
|---|---|---|
| Título vazio | `POST /eventos` com `"titulo": ""` | `422` |
| Capacidade zero/negativa | `"capacidade": 0` ou `-3` | `422` |
| Data inválida | `"data": "2026-02-30"` | `422` |
| E-mail inválido | `POST /participantes` com `"email": "abc"` | `422` |
| E-mail duplicado | `POST /participantes` repetindo `maria@email.com` | `409` `{"detail":"Já existe um participante cadastrado com este e-mail."}` |
| Excluir evento com inscrições | `DELETE /eventos/1` | `409` (mensagem pedindo para cancelar as inscrições) |
| Excluir participante com inscrições | `DELETE /participantes/1` | `409` |
| Cancelar e então excluir | `DELETE /eventos/1/inscricoes/1`, `DELETE /eventos/1/inscricoes/2`, `DELETE /eventos/1` | `204`, `204`, `204` |
| Reduzir capacidade abaixo dos inscritos | `PUT /eventos/1` com `capacidade: 1` havendo 2 inscritos | `409` |

## Cenários 9 a 12 — Relatórios

Os relatórios dependem dos dados. Siga uma destas opções.

### Opção A — dados de exemplo (`seed.py`)
Com a aplicação parada e o banco apagado, execute `python seed.py` (6 eventos, 8 participantes, 20 inscrições) e suba a API.

**9.** `GET /relatorios/eventos/ocupacao`

| evento_id | titulo | capacidade | total_inscritos | vagas_disponiveis | percentual_ocupacao |
|---|---|---|---|---|---|
| 1 | Introdução à Inteligência Artificial | 100 | 6 | 94 | 6.0 |
| 2 | Workshop de Python | 3 | 3 | 0 | 100.0 |
| 3 | Workshop de FastAPI | 5 | 3 | 2 | 60.0 |
| 4 | Minicurso de SQL | 20 | 3 | 17 | 15.0 |
| 5 | Seminário de Engenharia de Software | 50 | 5 | 45 | 10.0 |
| 6 | Maratona de Programação | 30 | 0 | 30 | 0.0 |

**10.** `GET /relatorios/eventos/categorias`

| categoria | total_eventos | capacidade_total | total_inscricoes |
|---|---|---|---|
| Competição | 1 | 30 | 0 |
| Minicurso | 1 | 20 | 3 |
| Palestra | 1 | 100 | 6 |
| Seminário | 1 | 50 | 5 |
| Workshop | 2 | 8 | 6 |

**11.** `GET /relatorios/participantes/cursos`

| curso | total_participantes | total_inscricoes |
|---|---|---|
| Análise e Desenvolvimento de Sistemas | 2 | 5 |
| Ciência da Computação | 2 | 5 |
| Engenharia de Software | 3 | 9 |
| Sistemas de Informação | 1 | 1 |

(Conferência: a soma das inscrições dos três relatórios é 20 em todos.)

### Opção B — dados criados à mão
Após P1–P4 e as inscrições do cenário 4, os relatórios refletem exatamente o que foi cadastrado (ex.: evento 1 com 1 inscrito de capacidade 2 → `50.0`).

## Cenário 12 — Relatórios acompanham as alterações

Com os dados do `seed.py`, faça cada passo e consulte de novo os relatórios:

1. `POST /eventos/6/inscricoes/1` (Maratona deixa de estar vazia)
   → ocupação do evento 6: `total_inscritos 1`, `vagas_disponiveis 29`, `percentual_ocupacao 3.33`; categoria *Competição*: `total_inscricoes 1`; curso *Engenharia de Software*: `total_inscricoes 10`.
2. `DELETE /eventos/6/inscricoes/1` → tudo volta ao valor anterior.
3. `PUT /eventos/3` com `capacidade: 10` → ocupação do evento 3: `vagas_disponiveis 7`, `percentual_ocupacao 30.0`; categoria *Workshop*: `capacidade_total 13`.
4. `DELETE /eventos/6` (sem inscrições) → o evento 6 some do relatório de ocupação e a categoria *Competição* desaparece do relatório por categoria.
5. `DELETE /eventos/2` → `409` (há inscrições); a ocupação do evento 2 continua `100.0`.

> Os valores acima foram calculados a partir dos dados do `seed.py`; confira com o que a API retornar.

## Testes automatizados

```bash
pip install -r requirements-dev.txt
pytest -v
```
