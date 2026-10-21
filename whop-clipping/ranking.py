#!/usr/bin/env python3
"""Ordena campanhas e resume ganhos a partir dos CSV desta pasta.

    python ranking.py                 # usa campanhas.csv e submissoes.csv
    python ranking.py --nicho gaming  # dá prioridade a um nicho

Fórmula: (orçamento total - pago) / clippers = dinheiro que "sobra" por clipper.
"""

import argparse
import csv
from pathlib import Path

PASTA = Path(__file__).resolve().parent
EVITAR = ("casino", "apostas", "gambling", "betting")


def numero(valor):
    try:
        return float(str(valor).replace("$", "").replace(",", ".").strip())
    except ValueError:
        return None


def ler(nome):
    caminho = PASTA / nome
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ranking_campanhas(nicho):
    linhas = []
    for c in ler("campanhas.csv"):
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
        linhas.append((bonus, restante / clippers, restante, c, avisos))
    linhas.sort(key=lambda l: (not l[4], l[0], l[1]), reverse=True)

    print("\n== Campanhas (restante ÷ clippers) ==")
    print(f"{'#':>2}  {'$/clipper':>9}  {'restante':>9}  {'CPM':>5}  campanha")
    for i, (bonus, por_clipper, restante, c, avisos) in enumerate(linhas, 1):
        extra = ("  ★ " + nicho if bonus else "") + ("  ⚠ " + ", ".join(avisos) if avisos else "")
        print(f"{i:>2}  {por_clipper:>9.0f}  {restante:>9.0f}  {c['cpm'] or '?':>5}  {c['campanha']}{extra}")


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
    args = ap.parse_args()
    ranking_campanhas(args.nicho)
    resumo_submissoes()
