#!/usr/bin/env python3
"""Ordena campanhas e resume ganhos a partir dos CSV desta pasta.

    python ranking.py                 # usa campanhas.csv e submissoes.csv
    python ranking.py --nicho gaming  # dá prioridade a um nicho
    python ranking.py --plataformas tiktok,youtube  # esconde as que não aceitam nenhuma
    python ranking.py --views 15000   # estima ganho por clip com 15K views
    python ranking.py --resumo        # grava resumo-AAAA-MM-DD.md da última semana

Fórmula: (orçamento total - pago) / clippers = dinheiro que "sobra" por clipper.
Cada execução junta as linhas de campanhas.csv a historico.csv (por data); com
dois registos da mesma campanha em datas diferentes mostra quando o orçamento esgota.
"""

import argparse
import csv
from datetime import date, timedelta
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


def views_medias():
    """Média de views dos teus clips em submissoes.csv (None se não houver)."""
    views = [numero(s["views_atuais"]) for s in ler("submissoes.csv")]
    views = [v for v in views if v]
    return sum(views) / len(views) if views else None


def ganho_estimado(campanha, restante, views):
    cpm = numero(campanha["cpm"])
    if not views or not cpm:
        return None
    return min(views * cpm / 1000, restante)


def ranking_campanhas(nicho, plataformas, views):
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
    if views:
        print(f"(ganho/clip estimado com {views:,.0f} views por clip)".replace(",", "."))
    print(f"{'#':>2}  {'$/clipper':>9}  {'restante':>9}  {'CPM':>5}  {'ganho/clip':>10}  {'esgota em':>9}  campanha")
    for i, (bonus, por_clipper, restante, c, avisos, esgota) in enumerate(linhas, 1):
        extra = ("  ★ " + nicho if bonus else "") + ("  ⚠ " + ", ".join(avisos) if avisos else "")
        ganho = ganho_estimado(c, restante, views)
        ganho_txt = f"${ganho:.2f}" if ganho is not None else "-"
        print(f"{i:>2}  {por_clipper:>9.0f}  {restante:>9.0f}  {c['cpm'] or '?':>5}  {ganho_txt:>10}  "
              f"{esgota or '-':>9}  {c['campanha']}{extra}")
    if escondidas:
        print(f"({escondidas} escondidas por não aceitarem {', '.join(plataformas)})")
    return linhas


def gravar_resumo(linhas, views):
    """Resumo da semana em Markdown, pronto a guardar ou partilhar."""
    hoje = date.today()
    inicio = hoje - timedelta(days=7)
    subs = [s for s in ler("submissoes.csv") if (data(s["data_publicacao"]) or hoje) >= inicio]
    ganho = sum(numero(s["ganho_usd"]) or 0 for s in subs)
    total_views = sum(numero(s["views_atuais"]) or 0 for s in subs)
    melhor = max(subs, key=lambda s: numero(s["views_atuais"]) or 0, default=None)

    r = [f"# Resumo da semana — {inicio:%d/%m} a {hoje:%d/%m/%Y}", "",
         f"- **Ganho:** ${ganho:.2f} em {len(subs)} clips",
         f"- **Views:** {total_views:,.0f}".replace(",", ".")]
    if melhor:
        r.append(f"- **Melhor clip:** {melhor['campanha']} ({melhor['plataforma']}) — "
                 f"{numero(melhor['views_atuais']) or 0:,.0f} views — {melhor['link']}".replace(",", "."))
    r += ["", "## Top 3 campanhas", ""]
    boas = [l for l in linhas if not l[4]][:3]
    for i, (bonus, por_clipper, restante, c, avisos, esgota) in enumerate(boas, 1):
        g = ganho_estimado(c, restante, views)
        r.append(f"{i}. **{c['campanha']}** — ${por_clipper:.0f}/clipper, CPM {c['cpm'] or '?'}"
                 + (f", ~${g:.2f}/clip" if g is not None else "")
                 + (f", esgota em {esgota}" if esgota else ""))
    if not boas:
        r.append("_Sem campanhas sem avisos — atualiza campanhas.csv._")
    alerta = [l[3]["campanha"] for l in linhas
              if l[5].startswith("~") and float(l[5][1:].split()[0]) < 7]
    if alerta:
        r += ["", "## ⚠ A esgotar (< 7 dias)", ""] + [f"- {a}" for a in alerta]
    caminho = PASTA / f"resumo-{hoje:%Y-%m-%d}.md"
    caminho.write_text("\n".join(r) + "\n", encoding="utf-8")
    print(f"\nResumo gravado em {caminho.name}")


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
    ap.add_argument("--views", default="",
                    help="views esperadas por clip (por defeito: a tua média em submissoes.csv)")
    ap.add_argument("--resumo", action="store_true", help="grava o resumo da semana em Markdown")
    args = ap.parse_args()
    plataformas = [p.strip().lower() for p in args.plataformas.split(",") if p.strip()]
    views = numero(args.views) or views_medias()
    linhas = ranking_campanhas(args.nicho, plataformas, views)
    resumo_submissoes()
    if args.resumo:
        gravar_resumo(linhas, views)
