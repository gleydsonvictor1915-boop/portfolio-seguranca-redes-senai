# Laboratório 01 — Consentimento e Eventos Web

Projeto educacional para portfólio de **segurança de redes e privacidade**. Demonstra o registro transparente de eventos em uma página local com consentimento explícito e revogável.

**Dados registrados:** apenas tipo de evento e data/hora UTC. **Não coletados:** IP, nome, e-mail, localização, digitação, histórico de navegação ou atividades fora desta página.

## Requisitos

Python 3.10 ou superior. Sem bibliotecas externas.

## Aula 1 — Rodar o laboratório

1. Abra um terminal na pasta do projeto.
2. Execute `python app.py` (ou `python3 app.py`).
3. Abra `http://127.0.0.1:8000` no **mesmo computador**.
4. Leia o consentimento e clique em **Concordo e quero testar**.
5. Clique em **Registrar clique de teste**.
6. Abra `http://127.0.0.1:8000/painel` e observe os eventos.
7. Clique em **Interromper coleta** para não registrar mais eventos nesta sessão.

## Aula 2 — Dados fictícios

Execute `python gerar_dados_demo.py`. Seis eventos sintéticos aparecerão no painel. Execute uma vez para evitar duplicações.

## Aula 3 — Testes automatizados

Execute `python -m unittest discover -s tests -v` e confirme três testes com resultado `OK`.

## Funcionamento e limites

- A página não registra a visita inicial. O primeiro registro só acontece após o clique de consentimento.
- O botão de teste gera o único outro evento permitido; o painel mostra agregações.
- A revogação impede novos eventos. Os registros anteriores podem ser apagados excluindo `eventos_local.db` **com o servidor desligado**.
- O banco local é ignorado pelo Git. Nunca publique informações pessoais de participantes.
- O servidor aceita conexões somente de `127.0.0.1`. Não exponha este código na internet: o painel de testes não tem autenticação.
- O GitHub armazena este código; o GitHub Pages não executa o backend Python.
- Um clique em um link não concede acesso às mensagens, câmera ou atividades externas ao navegador.

## Aprendizagem e portfólio

HTTP (200, 403), JavaScript, Python, SQLite, consentimento, privacidade e testes. O cenário de e-mail pode ser simulado enviando uma mensagem a você mesmo. O link local funciona somente no computador com o servidor iniciado.

## Arquitetura

```text
Navegador -> consentimento -> servidor HTTP local -> SQLite
Navegador <- painel de totais <-------------------------+
```
