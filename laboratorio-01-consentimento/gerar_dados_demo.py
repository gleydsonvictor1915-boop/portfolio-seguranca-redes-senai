"""Gera eventos fictícios para análise no painel."""
from datetime import datetime, timedelta, timezone
from app import inicializar_banco, registrar_evento

inicializar_banco()
agora = datetime.now(timezone.utc)
for horas, tipo in [
    (6, "consentimento_confirmado"),
    (5, "clique_botao_teste"),
    (4, "consentimento_confirmado"),
    (3, "clique_botao_teste"),
    (2, "clique_botao_teste"),
    (1, "consentimento_confirmado"),
]:
    registrar_evento(tipo, (agora - timedelta(hours=horas)).isoformat(timespec="seconds"))
print("6 eventos fictícios adicionados ao banco local.")
