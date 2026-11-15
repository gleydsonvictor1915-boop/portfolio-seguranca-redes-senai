"""Servidor local de demonstração de consentimento e eventos mínimos."""
import json
import secrets
import sqlite3
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "eventos_local.db"
TOKENS = set()
TOKENS_LOCK = Lock()

def inicializar_banco():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, data_utc TEXT NOT NULL)")

def registrar_evento(tipo, data_utc=None):
    if tipo not in {"consentimento_confirmado", "clique_botao_teste"}:
        raise ValueError("Evento não permitido")
    data_utc = data_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO eventos(tipo, data_utc) VALUES (?, ?)", (tipo, data_utc))

def resumo():
    with sqlite3.connect(DB_PATH) as db:
        contagens = dict(db.execute("SELECT tipo, COUNT(*) FROM eventos GROUP BY tipo").fetchall())
        ultimos = db.execute("SELECT tipo, data_utc FROM eventos ORDER BY id DESC LIMIT 20").fetchall()
    return contagens, ultimos

class LaboratorioHandler(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        return

    def responder(self, codigo, conteudo, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(conteudo)

    def json(self, codigo, dados):
        self.responder(codigo, json.dumps(dados, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        caminho = urlsplit(self.path).path
        arquivos = {
            "/": (BASE / "templates/index.html", "text/html; charset=utf-8"),
            "/static/app.js": (BASE / "static/app.js", "application/javascript; charset=utf-8"),
            "/static/style.css": (BASE / "static/style.css", "text/css; charset=utf-8"),
        }
        if caminho in arquivos:
            arquivo, mime = arquivos[caminho]
            self.responder(200, arquivo.read_bytes(), mime)
            return
        if caminho == "/painel":
            contagens, ultimos = resumo()
            linhas = "".join(f"<tr><td>{escape(tipo)}</td><td>{escape(data)}</td></tr>" for tipo, data in ultimos) or '<tr><td colspan="2">Nenhum evento registrado.</td></tr>'
            html = (BASE / "templates/painel.html").read_text(encoding="utf-8")
            html = html.replace("{{TOTAL}}", str(sum(contagens.values()))).replace("{{CONSENTIMENTOS}}", str(contagens.get("consentimento_confirmado", 0))).replace("{{CLIQUES}}", str(contagens.get("clique_botao_teste", 0))).replace("{{LINHAS}}", linhas)
            self.responder(200, html.encode(), "text/html; charset=utf-8")
            return
        self.json(404, {"erro": "Rota não encontrada"})

    def do_POST(self):
        caminho = urlsplit(self.path).path
        if caminho not in {"/api/consentimento", "/api/eventos", "/api/revogar"}:
            self.json(404, {"erro": "Rota não encontrada"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.json(415, {"erro": "Use application/json"})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho < 1 or tamanho > 1024:
                self.json(413, {"erro": "Corpo inválido"})
                return
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise ValueError("JSON esperado")
        except (ValueError, json.JSONDecodeError):
            self.json(400, {"erro": "JSON inválido"})
            return
        if caminho == "/api/consentimento":
            token = secrets.token_urlsafe(32)
            with TOKENS_LOCK:
                TOKENS.add(token)
            registrar_evento("consentimento_confirmado")
            self.json(200, {"token": token, "mensagem": "Consentimento registrado"})
            return
        token = dados.get("token")
        with TOKENS_LOCK:
            autorizado = isinstance(token, str) and token in TOKENS
            if autorizado and caminho == "/api/revogar":
                TOKENS.discard(token)
        if not autorizado:
            self.json(403, {"erro": "Consentimento necessário"})
            return
        if caminho == "/api/revogar":
            self.json(200, {"mensagem": "Coleta interrompida"})
            return
        if dados.get("tipo") != "clique_botao_teste":
            self.json(400, {"erro": "Tipo não permitido"})
            return
        registrar_evento("clique_botao_teste")
        self.json(200, {"mensagem": "Clique registrado"})

def criar_servidor(porta=8000):
    inicializar_banco()
    return ThreadingHTTPServer(("127.0.0.1", porta), LaboratorioHandler)

if __name__ == "__main__":
    servidor = criar_servidor()
    print("Página: http://127.0.0.1:8000")
    print("Painel: http://127.0.0.1:8000/painel")
    print("Somente local. Pare com Ctrl+C.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
