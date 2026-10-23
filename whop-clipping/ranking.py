#!/usr/bin/env python3
"""Ordena campanhas e resume ganhos a partir dos CSV desta pasta.

    python ranking.py                 # usa campanhas.csv e submissoes.csv
    python ranking.py --nicho gaming  # dá prioridade a um nicho
    python ranking.py --plataformas tiktok,youtube  # esconde as que não aceitam nenhuma

Fórmula: (orçamento total - pago) / clippers = dinheiro que "sobra" por clipper.
Cada execução junta as linhas de campanhas.csv a historico.csv (por data); com
dois registos da mesma campanha em datas diferentes mostra quando o orçamento esgota.
"""

import argparse
import csv
from datetime import date
from pathlib import Path

PASTA = Path(__file__).resolve().parent
EVITAR = ("casino", "apostas", "gambling", "betting")


def numero(valor):
    """Aceita 35500, $35,500, 35.500, 1,75, $5K, 1.2M."""
    texto = str(valor or "").replace("$", "").replace("US", "").replace(" ", "").strip().upper()
    mult = 1
    if texto[-1:] in ("K", "M"):
        mult = 1_000 if texto[-1] == "K" else 1_000_000
        texto = texto[:-1]
    if "," in texto and "." in texto:
        # o último separador é o decimal
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto or "." in texto:
        sep = "," if "," in texto else "."
        partes = texto.split(sep)
        if len(partes) > 2 or len(partes[-1]) == 3:
            texto = texto.replace(sep, "")  # separador de milhares
        else:
            texto = texto.replace(",", ".")
    try:
        return float(texto) * mult
    except ValueError:
        return None


def data(valor):
    try:
        return date.fromisoformat(str(valor).strip())
    except ValueError:
        return None


def ler(nome):
    caminho = PASTA / nome
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def aceita(campanha, plataformas):
    if not plataformas or not campanha["plataformas"].strip():
        return True  # sem filtro ou sem info: não esconder
    aceites = campanha["plataformas"].lower()
    return any(p in aceites for p in plataformas)


def atualizar_historico(campanhas):
    """Junta as campanhas a historico.csv (sem repetir a mesma campanha na mesma data)."""
    caminho = PASTA / "historico.csv"
    historico = ler("historico.csv")
    vistos = {(h["data"], h["campanha"]) for h in historico}
    novos = [c for c in campanhas if c.get("data") and (c["data"], c["campanha"]) not in vistos]
    if novos:
        campos = list(campanhas[0].keys())
        escrever_cabecalho = not caminho.exists()
        with caminho.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            if escrever_cabecalho:
                w.writeheader()
            w.writerows(novos)
        historico += novos
    return historico


def previsao(campanha, restante, historico):
    """Dias até o orçamento esgotar, pelo registo anterior mais recente."""
    hoje = data(campanha.get("data"))
    if not hoje:
        return ""
    anteriores = [h for h in historico if h["campanha"] == campanha["campanha"]
                  and data(h["data"]) and data(h["data"]) < hoje]
    if not anteriores:
        return ""
    antes = max(anteriores, key=lambda h: data(h["data"]))
    pago_antes, total_antes = numero(antes["orcamento_pago"]), numero(antes["orcamento_total"])
    if pago_antes is None or not total_antes:
        return ""
    dias = (hoje - data(antes["data"])).days
    gasto_dia = ((numero(campanha["orcamento_total"]) - restante) - pago_antes) / dias
    if gasto_dia <= 0:
        return "parada"
    return f"~{restante / gasto_dia:.0f} dias"


def ranking_campanhas(nicho, plataformas):
    linhas = []
    escondidas = 0
    campanhas = ler("campanhas.csv")
    historico = atualizar_historico(campanhas) if campanhas else []
    for c in campanhas:
        if not aceita(c, plataformas):
            escondidas += 1
            continue
        total, pago, clippers = numero(c["orcamento_total"]), numero(c["orcamento_pago"]), numero(c["clippers"])
        if not total or pago is None or not clippers:
            continue
        restante = total - pago
        avisos = []
        if restante / total < 0.2:
            avisos.append("<20% orçamento")
        if any(p in c["nicho"].lower() for p in EVITAR):
            avisos.append("casino")
        bonus = bool(nicho) and nicho.lower() in c["nicho"].lower()
        linhas.append((bonus, restante / clippers, restante, c, avisos, previsao(c, restante, historico)))
    linhas.sort(key=lambda l: (not l[4], l[0], l[1]), reverse=True)

    print("\n== Campanhas (restante ÷ clippers) ==")
    print(f"{'#':>2}  {'$/clipper':>9}  {'restante':>9}  {'CPM':>5}  {'esgota em':>9}  campanha")
    for i, (bonus, por_clipper, restante, c, avisos, esgota) in enumerate(linhas, 1):
        extra = ("  ★ " + nicho if bonus else "") + ("  ⚠ " + ", ".join(avisos) if avisos else "")
        print(f"{i:>2}  {por_clipper:>9.0f}  {restante:>9.0f}  {c['cpm'] or '?':>5}  {esgota or '-':>9}  "
              f"{c['campanha']}{extra}")
    if escondidas:
        print(f"({escondidas} escondidas por não aceitarem {', '.join(plataformas)})")


def resumo_submissoes():
    subs = ler("submissoes.csv")
    if not subs:
        print("\n(submissoes.csv vazio — regista os teus clips para veres o resumo)")
        return
    subs.sort(key=lambda s: numero(s["views_atuais"]) or 0, reverse=True)
    print("\n== Submissões por views ==")
    for s in subs:
        print(f"{numero(s['views_atuais']) or 0:>10.0f} views  ${numero(s['ganho_usd']) or 0:>7.2f}  "
              f"{s['campanha']} ({s['plataforma']}) {s['link']}")
    total = sum(numero(s["ganho_usd"]) or 0 for s in subs)
    print(f"\nTotal ganho: ${total:.2f} em {len(subs)} clips")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nicho", default="gaming", help="nicho a destacar (default: gaming)")
    ap.add_argument("--plataformas", default="",
                    help="onde publicas, separado por vírgulas (ex.: tiktok,instagram,youtube)")
    args = ap.parse_args()
    plataformas = [p.strip().lower() for p in args.plataformas.split(",") if p.strip()]
    ranking_campanhas(args.nicho, plataformas)
    resumo_submissoes()
