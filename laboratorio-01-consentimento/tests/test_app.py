"""Testes do consentimento e da minimização de dados."""
import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import app as laboratorio

class TesteLaboratorio(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        laboratorio.DB_PATH = Path(self.pasta.name) / "eventos_testes.db"
        with laboratorio.TOKENS_LOCK:
            laboratorio.TOKENS.clear()
        self.servidor = laboratorio.criar_servidor(porta=0)
        self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.servidor.server_port}"

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join(timeout=2)
        self.pasta.cleanup()

    def postar(self, rota, dados):
        pedido = Request(self.url + rota, data=json.dumps(dados).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(pedido, timeout=3) as resposta:
                return resposta.status, json.load(resposta)
        except HTTPError as erro:
            return erro.code, json.loads(erro.read())

    def test_bloqueia_evento_sem_consentimento(self):
        codigo, _ = self.postar("/api/eventos", {"token": "falso", "tipo": "clique_botao_teste"})
        self.assertEqual(codigo, 403)
        contagem, _ = laboratorio.resumo()
        self.assertEqual(contagem, {})

    def test_consentimento_clique_e_revogacao(self):
        codigo, dados = self.postar("/api/consentimento", {})
        self.assertEqual(codigo, 200)
        token = dados["token"]
        codigo, _ = self.postar("/api/eventos", {"token": token, "tipo": "clique_botao_teste"})
        self.assertEqual(codigo, 200)
        codigo, _ = self.postar("/api/revogar", {"token": token})
        self.assertEqual(codigo, 200)
        codigo, _ = self.postar("/api/eventos", {"token": token, "tipo": "clique_botao_teste"})
        self.assertEqual(codigo, 403)
        contagens, _ = laboratorio.resumo()
        self.assertEqual(contagens["consentimento_confirmado"], 1)
        self.assertEqual(contagens["clique_botao_teste"], 1)

    def test_nao_grava_identificadores_pessoais(self):
        with sqlite3.connect(laboratorio.DB_PATH) as banco:
            colunas = [r[1] for r in banco.execute("PRAGMA table_info(eventos)")]
        self.assertEqual(colunas, ["id", "tipo", "data_utc"])

if __name__ == "__main__":
    unittest.main()
