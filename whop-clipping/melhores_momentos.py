#!/usr/bin/env python3
"""Encontra os melhores momentos de um vídeo longo para fazer clips.

Fluxo: descarrega (yt-dlp) -> transcreve (faster-whisper) -> mede o volume
(ffmpeg) -> pontua janelas de 15-45 s -> escolhe as melhores sem sobreposição.
Opcionalmente corta os clips em 9:16 com legendas queimadas.

Exemplos:
    python melhores_momentos.py "https://youtube.com/watch?v=..."
    python melhores_momentos.py stream.mp4 --top 10 --cortar --vertical --legendas
    python melhores_momentos.py stream.mp4 --palavras "warhammer,space marine,heresia"

Requisitos (grátis): ffmpeg no PATH e `pip install faster-whisper yt-dlp`.
"""

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path

# Palavras que costumam indicar um bom gancho (PT + EN).
PALAVRAS_GANCHO = [
    # português
    "nunca", "ninguém", "ninguem", "segredo", "verdade", "incrível", "incrivel",
    "louco", "loucura", "impossível", "impossivel", "pior", "melhor", "erro",
    "mentira", "dinheiro", "milhões", "milhoes", "porquê",
    "olha", "espera", "atenção", "atencao", "sério", "serio", "ridículo",
    "ridiculo", "polémica", "polemica", "odeio", "adoro", "chocante", "primeira vez",
    "não acredito", "nao acredito", "o problema", "ninguém fala", "a razão",
    # inglês
    "never", "nobody", "secret", "truth", "insane", "crazy", "impossible",
    "worst", "best", "mistake", "lie", "money", "million", "why", "wait",
    "look", "seriously", "hate", "love", "shocking", "first time", "can't believe",
    "the problem", "no one", "the reason", "what the", "oh my god", "let's go",
]

RE_NUMERO = re.compile(r"\b\d+[\d.,]*\s*(%|k|mil|milhões|million|euros?|dólares|dollars|\$)?", re.I)
FIM_FRASE = (".", "!", "?", "…")


def correr(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def obter_video(fonte: str, pasta: Path) -> Path:
    if Path(fonte).exists():
        return Path(fonte).resolve()
    if not re.match(r"^https?://", fonte):
        sys.exit(f"Fonte não encontrada: {fonte}")
    try:
        import yt_dlp
    except ImportError:
        sys.exit("Falta o yt-dlp: pip install yt-dlp")
    print(f"[1/4] A descarregar {fonte} ...")
    opcoes = {
        "outtmpl": str(pasta / "video.%(ext)s"),
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(fonte, download=True)
        return Path(ydl.prepare_filename(info)).with_suffix(".mp4")


def extrair_audio(video: Path, pasta: Path) -> Path:
    wav = pasta / "audio16k.wav"
    correr(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1",
            "-ar", "16000", str(wav)])
    return wav


def volume_por_segundo(wav: Path) -> list[float]:
    """Nível RMS (dB) de cada segundo de áudio."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(wav), "-af",
         "asetnsamples=16000,astats=metadata=1:reset=1,"
         "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
         "-f", "null", "-"],
        text=True, capture_output=True, check=True)
    niveis = []
    for linha in r.stdout.splitlines():
        if "RMS_level=" in linha:
            v = linha.split("=", 1)[1]
            niveis.append(-90.0 if v in ("-inf", "inf", "nan") else max(float(v), -90.0))
    return niveis


def transcrever(wav: Path, modelo: str, idioma: str | None, gpu: bool = False):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Falta o faster-whisper: pip install faster-whisper")
    print(f"[2/4] A transcrever com o modelo '{modelo}' (pode demorar) ...")
    # CPU por defeito: no Windows a GPU precisa de CUDA/cuDNN instalados à parte.
    m = WhisperModel(modelo, device="cuda" if gpu else "cpu",
                     compute_type="float16" if gpu else "int8")
    segs, info = m.transcribe(str(wav), language=idioma, vad_filter=True,
                              word_timestamps=True)
    resultado = []
    for s in segs:
        palavras = [{"w": p.word.strip(), "ini": p.start, "fim": p.end}
                    for p in (s.words or []) if p.word.strip()]
        resultado.append({"ini": s.start, "fim": s.end, "texto": s.text.strip(),
                          "palavras": palavras})
        print(f"    {fmt(s.start)}  {s.text.strip()[:80]}", flush=True)
    return resultado, info.language


def contar_ganchos(texto: str, ganchos: list[str]) -> int:
    t = texto.lower()
    return sum(t.count(g) for g in ganchos)


def pontuar_gancho(texto: str, ganchos: list[str]) -> float:
    p = 3.0 * min(contar_ganchos(texto, ganchos), 2)
    p += 2.0 if "?" in texto else 0
    p += 1.0 if "!" in texto else 0
    p += 1.0 if RE_NUMERO.search(texto) else 0
    p += 1.0 if len(texto.split()) <= 14 else 0
    return p


def zscore(v, media, desvio):
    return 0.0 if desvio == 0 else (v - media) / desvio


def candidatos(segs, dmin, dmax):
    for i in range(len(segs)):
        for j in range(i, len(segs)):
            dur = segs[j]["fim"] - segs[i]["ini"]
            if dur > dmax:
                break
            if dur >= dmin:
                yield i, j


def pontuar(segs, niveis, ganchos, dmin, dmax):
    vol_medio = statistics.fmean(niveis) if niveis else 0
    vol_desvio = statistics.pstdev(niveis) if len(niveis) > 1 else 0
    ritmos = [len(s["texto"].split()) / max(s["fim"] - s["ini"], 0.5) for s in segs]
    ritmo_medio = statistics.fmean(ritmos) if ritmos else 0
    ritmo_desvio = statistics.pstdev(ritmos) if len(ritmos) > 1 else 0

    lista = []
    for i, j in candidatos(segs, dmin, dmax):
        ini, fim = segs[i]["ini"], segs[j]["fim"]
        texto = " ".join(s["texto"] for s in segs[i:j + 1])
        n_palavras = len(texto.split())
        dur = fim - ini

        gancho = pontuar_gancho(segs[i]["texto"], ganchos)
        # Palavras-gancho por 100 palavras, limitado para não abafar o resto.
        densidade = min(contar_ganchos(texto, ganchos) / max(n_palavras, 1) * 100, 5.0)
        ritmo = zscore(n_palavras / dur, ritmo_medio, ritmo_desvio)
        janela = niveis[int(ini):int(math.ceil(fim))] or [vol_medio]
        volume = zscore(statistics.fmean(janela), vol_medio, vol_desvio)
        pico = zscore(max(janela), vol_medio, vol_desvio)
        fecho = 1.0 if segs[j]["texto"].endswith(FIM_FRASE) else 0.0
        # Clips de 20-35 s tendem a reter melhor.
        duracao = 1.0 if 20 <= dur <= 35 else 0.0

        total = (2.0 * gancho + 1.0 * densidade + 1.0 * ritmo
                 + 1.5 * volume + 0.5 * pico + fecho + duracao)
        lista.append({
            "ini": round(ini, 2), "fim": round(fim, 2), "duracao": round(dur, 1),
            "pontuacao": round(total, 2), "gancho": segs[i]["texto"],
            "texto": texto, "i": i, "j": j,
            "detalhe": {"gancho": gancho, "densidade": round(densidade, 2),
                        "ritmo": round(ritmo, 2), "volume": round(volume, 2),
                        "pico": round(pico, 2)},
        })
    return lista


def escolher(lista, top, folga=5.0):
    escolhidos = []
    for c in sorted(lista, key=lambda c: c["pontuacao"], reverse=True):
        if all(c["fim"] + folga <= e["ini"] or c["ini"] >= e["fim"] + folga
               for e in escolhidos):
            escolhidos.append(c)
        if len(escolhidos) == top:
            break
    return escolhidos


def fmt(seg, srt=False):
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"


def escrever_srt(segs, clip, destino: Path, por_linha=3):
    """Legendas curtas (3 palavras) ao estilo TikTok, com tempos relativos ao clip."""
    palavras = [p for s in segs[clip["i"]:clip["j"] + 1] for p in s["palavras"]]
    linhas = []
    for k in range(0, len(palavras), por_linha):
        grupo = palavras[k:k + por_linha]
        ini = max(grupo[0]["ini"] - clip["ini"], 0)
        fim = max(grupo[-1]["fim"] - clip["ini"], ini + 0.2)
        texto = " ".join(p["w"] for p in grupo).upper()
        linhas.append(f"{len(linhas) + 1}\n{fmt(ini, True)} --> {fmt(fim, True)}\n{texto}\n")
    destino.write_text("\n".join(linhas), encoding="utf-8")


def cortar(video: Path, clip, saida: Path, vertical: bool, srt: Path | None):
    filtros = []
    if vertical:
        filtros.append("crop='min(iw,ih*9/16)':ih,scale=1080:1920")
    if srt:
        caminho = str(srt.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        filtros.append(
            f"subtitles='{caminho}':force_style='FontName=Arial,Bold=1,FontSize=16,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,"
            "Outline=3,Shadow=0,Alignment=2,MarginV=70'")
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(clip["ini"]), "-i", str(video),
           "-t", str(clip["duracao"])]
    if filtros:
        cmd += ["-vf", ",".join(filtros)]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(saida)]
    correr(cmd)


def main():
    ap = argparse.ArgumentParser(description="Encontra os melhores momentos para clips.")
    ap.add_argument("fonte", help="Link (YouTube, Twitch, Kick...) ou ficheiro de vídeo")
    ap.add_argument("--top", type=int, default=8, help="Nº de momentos (padrão 8)")
    ap.add_argument("--min", type=float, default=15, help="Duração mínima em s (padrão 15)")
    ap.add_argument("--max", type=float, default=45, help="Duração máxima em s (padrão 45)")
    ap.add_argument("--modelo", default="small",
                    help="Modelo Whisper: tiny, base, small, medium, large-v3 (padrão small)")
    ap.add_argument("--idioma", default=None, help="pt, en... (padrão: deteta sozinho)")
    ap.add_argument("--palavras", default="",
                    help="Palavras extra do nicho, separadas por vírgulas")
    ap.add_argument("--saida", default="momentos", help="Pasta de saída (padrão ./momentos)")
    ap.add_argument("--cortar", action="store_true", help="Exporta cada momento em MP4")
    ap.add_argument("--vertical", action="store_true", help="Corta ao centro para 9:16")
    ap.add_argument("--legendas", action="store_true", help="Queima legendas no vídeo")
    ap.add_argument("--gpu", action="store_true", help="Usa a placa NVIDIA (precisa de CUDA)")
    a = ap.parse_args()

    pasta = Path(a.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    ganchos = PALAVRAS_GANCHO + [p.strip().lower() for p in a.palavras.split(",") if p.strip()]

    video = obter_video(a.fonte, pasta)
    wav = extrair_audio(video, pasta)
    segs, idioma = transcrever(wav, a.modelo, a.idioma, a.gpu)
    if not segs:
        sys.exit("Não foi encontrada fala no vídeo.")

    print("[3/4] A medir o volume e a pontuar momentos ...")
    niveis = volume_por_segundo(wav)
    escolhidos = escolher(pontuar(segs, niveis, ganchos, a.min, a.max), a.top)
    escolhidos.sort(key=lambda c: c["ini"])

    print("[4/4] A gravar resultados ...")
    rel = [f"# Melhores momentos — {video.name}\n",
           f"Idioma: {idioma} · {len(escolhidos)} momentos\n"]
    ranking = sorted(escolhidos, key=lambda c: c["pontuacao"], reverse=True)
    for n, c in enumerate(escolhidos, 1):
        c["posicao"] = ranking.index(c) + 1
        srt = pasta / f"clip_{n:02d}.srt"
        escrever_srt(segs, c, srt)
        if a.cortar:
            mp4 = pasta / f"clip_{n:02d}.mp4"
            print(f"    a cortar {mp4.name} ({fmt(c['ini'])}–{fmt(c['fim'])})")
            cortar(video, c, mp4, a.vertical, srt if a.legendas else None)
        rel += [f"\n## Clip {n:02d} — {fmt(c['ini'])} → {fmt(c['fim'])} "
                f"({c['duracao']} s) · #{c['posicao']} · pontuação {c['pontuacao']}\n",
                f"**Gancho:** {c['gancho']}\n",
                f"> {c['texto']}\n"]

    (pasta / "momentos.md").write_text("\n".join(rel), encoding="utf-8")
    limpo = [{k: v for k, v in c.items() if k not in ("i", "j")} for c in escolhidos]
    (pasta / "momentos.json").write_text(json.dumps(limpo, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    (pasta / "transcricao.txt").write_text(
        "\n".join(f"[{fmt(s['ini'])}] {s['texto']}" for s in segs), encoding="utf-8")
    wav.unlink(missing_ok=True)

    print("\nTop momentos:")
    for c in ranking:
        print(f"  #{c['posicao']}  {fmt(c['ini'])}–{fmt(c['fim'])}  "
              f"({c['pontuacao']})  {c['gancho'][:70]}")
    print(f"\nResultados em {pasta.resolve()}/ (momentos.md, momentos.json, .srt"
          f"{', .mp4' if a.cortar else ''})")


if __name__ == "__main__":
    main()
