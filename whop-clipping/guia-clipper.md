# Guia do Clipper — Whop Content Rewards

> Pesquisa feita a 16/10/2026. As taxas e orçamentos mudam todos os dias —
> confirma sempre no quadro de Content Rewards do Whop antes de entrar numa campanha.

---

## 1. Como escolher campanhas (a regra principal)

**Não escolhas pelo CPM mais alto. Escolhe pelo dinheiro que ainda vais conseguir receber.**

Para cada campanha, vê estes 5 números:

| O quê | Porquê | Bom sinal |
|---|---|---|
| **CPM** ($ por 1.000 views) | Quanto ganhas por view | ≥ $1,00 |
| **Orçamento restante** | Quando acaba, deixas de ser pago — mesmo com views | ≥ $20.000 |
| **Nº de clippers** | Mais clippers = orçamento acaba mais depressa | Poucos clippers para o orçamento |
| **Material dado** | Com material pronto produzes 3–5× mais rápido | Pasta com vídeos longos/streams |
| **Nicho** | Tens de conseguir fazer clips virais desse tema | Gaming / entretenimento (já tens experiência com o Warhammer) |

**Fórmula rápida:** `orçamento restante ÷ nº de clippers` = quanto "sobra" por clipper.
Exemplo: $35.500 ÷ 104 clippers ≈ $341 por clipper → bom. $64.900 ÷ 842 ≈ $77 → saturado.

**Evita:**
- Campanhas com < 20% do orçamento restante (podes fazer views e não receber).
- Campanhas de casino/apostas (pagam mais, mas regras rígidas, orçamentos voláteis e risco de banir contas).
- Campanhas sem material — obrigam-te a procurar conteúdo e perdes horas.

---

## 2. Campanhas vistas em outubro de 2026 (fonte externa — confirmar no Whop)

| Campanha | CPM | Restante | Clippers | Avaliação |
|---|---|---|---|---|
| **DIGGER x ClipFarm** | $1,50 | ~$35.500 | 104 | ⭐ Melhor: bom CPM, muito orçamento, pouca concorrência |
| **Boxabl x ASG** | $2,00 | ~$9.800 | ? | Bom CPM, mas orçamento curto — entra já ou ignora |
| **Mini Brand Vinyl Cafe Event** | $1,75 | ? | ? | Ver orçamento e material |
| **Boxabl Official (Clip Farm)** | $0,50 | ~$64.900 | 842 | Saturado e CPM baixo — evitar |
| **Roobet** | $1,50 | $250k (data incerta) | ? | Casino — só com conta dedicada, ler regras |

Plano: **1 campanha principal** (a melhor pela fórmula) + **1 secundária de gaming**, para não depender de um só orçamento.

---

## 3. Regras de dinheiro que tens de saber

- **Comissão**: as fontes falam em ~7–10% sobre os pagamentos (não concordam quem paga) — confirma nos termos.
- **Retenção**: o pagamento fica preso ~10 dias antes de ser libertado.
- **Aprovação**: as marcas têm ~48h para aprovar; podem rejeitar depois por suspeita de bots.
- **Limites por clip**: muitas campanhas têm máximo por vídeo (ex. $100–$1.000) e mínimo de views.
- **Orçamento acaba por ordem de chegada** — publicar cedo numa campanha nova vale mais.

---

## 4. Ferramentas

### O que já temos ligado

| Ferramenta | Para quê | Estado |
|---|---|---|
| **HyperFrames** (skills instalados neste repositório) | Legendas animadas (`embedded-captions`), grafismos sobre vídeo (`talking-head-recut`), títulos/motion (`motion-graphics`), transcrição e remoção de fundo pelo CLI | ✅ Grátis, corre localmente (precisa de Node + ffmpeg no PC) |
| **Higgsfield** | Shorts Studio, reframe 16:9 → 9:16, previsão de viralidade, música trending do TikTok, **publicar direto no TikTok**, dobragem para outras línguas | ⚠️ Plano grátis, **0 créditos** |
| **Everygen** | Encontrar clips num vídeo longo (`find_clips`), cortar, legendas, remover legendas, descarregar vídeos, analisar vídeos | ⚠️ **0 créditos** |
| **Canva** | Capas/thumbnails e textos para os clips | ✅ Ligado |
| **Google Calendar** | Agenda de publicação (ex. 3 clips/dia) | ✅ Ligado |
| **Gmail** | — | ❌ Acesso recusado (reconectar) |

### Ferramentas grátis recomendadas

| Ferramenta | Para quê | Limite grátis |
|---|---|---|
| **CapCut** (PC/telemóvel) | Editor principal: cortes, legendas automáticas, 9:16 | Legendas auto até ~10 min por vídeo; 1080p sem marca de água nos templates base |
| **yt-dlp** | Descarregar o material/streams da campanha | Grátis, sem limites |
| **ffmpeg** | Cortar e converter em lote, muito rápido | Grátis |
| **faster-whisper** | Transcrever o vídeo inteiro → encontrar os momentos bons por texto | Grátis, local |
| **2short.ai** | Encontrar momentos virais automaticamente em vídeos do YouTube | ~30 min de análise/mês |
| **OpusClip** | Clips automáticos com legendas | Plano grátis limitado (confirmar) |
| **OpenClip** | Legendas, transcrição, compressão no browser | Ferramentas base grátis; clipping 100 min uma vez |

**Stack recomendado a custo zero:**
`yt-dlp` (descarregar) → `faster-whisper` (transcrever e achar ganchos) → `ffmpeg` (cortar) → **CapCut** ou **HyperFrames** (legendas e acabamento) → publicar.

---

## 5. Rotina diária de produção

1. **Manhã (20 min):** ver campanhas novas no Whop e aplicar a fórmula da secção 1.
2. **Descarregar e transcrever** o material novo.
3. **Escolher 5–8 momentos** pela transcrição: frases polémicas, reações fortes, números chocantes, piadas.
4. **Cortar** clips de 15–45 s, gancho nos primeiros 2–3 s.
5. **Legendas grandes** com palavras-chave a cor; sem marcas de água de apps.
6. **Publicar** 1–3 clips por conta por dia, espaçados; variar ganchos do mesmo momento.
7. **Submeter no Whop logo após publicar** (orçamento é por ordem de chegada).
8. **Ao fim de 48h:** registar views de cada clip numa folha e repetir o que funcionou.

---

## 6. Fontes

- [Whop Docs — Content Rewards](https://docs.whop.com/memberships-and-access/third-party-apps/content-rewards)
- [Shopiator — Top Whop Clipping Offers Oct 2026](https://shopiator.com/blog/top-whop-clipping-offers)
- [OpenClip — Whop Clipping Guide 2026](https://openclip.app/guides/whop-clipping-guide)
- [ClipSpeed — Fee e hold de 10 dias](https://www.clipspeed.ai/blog/whop-content-rewards-clipping-guide.html)
- [Sirency — Whop Content Rewards Clipping](https://www.sirency.com/blog/whop-content-rewards-clipping)
- [ClipAffiliates — É legítimo?](https://www.clipaffiliates.com/blog/is-whop-content-rewards-legit)
- [Forkoff — Custos para marcas 2026](https://forkoff.xyz/blog/clipping/whop-content-rewards-brand-cost-2026)
- [OpenClip — Alternativas ao CapCut](https://openclip.app/alternatives/capcut-alternatives-for-shorts.md)
- [OpenClip — Alternativas ao 2short.ai](https://openclip.app/alternatives/2short-alternatives)

---

## 7. Script: encontrar os melhores momentos (`melhores_momentos.py`)

Instalar uma vez (grátis):
```bash
# ffmpeg: https://ffmpeg.org/download.html (Windows: winget install ffmpeg)
pip install faster-whisper yt-dlp
```

Usar:
```bash
# Só listar os melhores momentos (com tempos e texto)
python melhores_momentos.py "https://www.youtube.com/watch?v=..."

# Exportar já os clips em 9:16 com legendas
python melhores_momentos.py stream.mp4 --top 10 --cortar --vertical --legendas

# Dar palavras do nicho para pesarem mais
python melhores_momentos.py stream.mp4 --palavras "warhammer,space marine,heresia" --idioma pt
```

Gera na pasta `momentos/`: `momentos.md` (relatório), `momentos.json`, `transcricao.txt`, um `.srt` por clip e, com `--cortar`, um `.mp4` por clip.

Como pontua cada janela de 15–45 s: gancho na primeira frase (palavras fortes, pergunta, número, frase curta), densidade de palavras-gancho, ritmo de fala, volume/gritos acima da média, termina numa frase completa e duração de 20–35 s.

Dicas: `--modelo tiny` é muito rápido para testar; `--modelo medium` transcreve melhor em português. O corte 9:16 é ao centro — se a ação estiver de lado, ajusta no CapCut.

---

## 8. Análise semanal (campanhas + ganhos)

### Como abrir o Claude com acesso ao Whop
Uma conversa do Claude Code **na cloud** (web/telemóvel) **não vê o teu Chrome**. Para o Claude ler o Whop com o teu login, usa uma destas opções:
- o **painel Claude no Chrome** (extensão Claude in Chrome) — o mais simples;
- uma conversa aberta na **app Claude Desktop** no PC, com o Chrome ligado.

### Prompt pronto a colar (painel Claude no Chrome)
> Estou no Whop → Content Rewards. Percorre todas as campanhas ativas e faz uma tabela CSV com as colunas
> `data,campanha,cpm,orcamento_total,orcamento_pago,clippers,nicho,material,plataformas,link`.
> Depois abre as minhas submissões e ganhos e faz outra tabela CSV com
> `data_publicacao,campanha,plataforma,link,views_48h,views_atuais,ganho_usd,estado`.

Cola o resultado em `campanhas.csv` e `submissoes.csv` (nesta pasta) e corre:
```bash
python ranking.py               # destaca gaming por defeito
python ranking.py --nicho warhammer
```
O script ordena por `(total − pago) ÷ clippers`, marca ⚠ campanhas com < 20% de orçamento ou de casino, e lista os teus clips por views com o total ganho.

> Nota: no cartão do Whop, `$5K/$6K` costuma ser **pago / total** (a barra mostra o gasto). Confirma ao abrir a campanha.
