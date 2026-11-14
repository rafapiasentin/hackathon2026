"""API do assistente de leis de Londrina (protótipo).

Lê o leis.json em memória (sem precisar do Postgres) e atende o contrato do front (frontend/src/api/types.ts):
    POST /api/perguntar        {"pergunta": "..."}  -> Resposta {resposta, fontes, ignoradas}
    GET  /api/leis             ?q=&pagina=&numero=&ano=&situacao=  -> {total, pagina, itens}
    GET  /api/leis/{id}        -> Lei (com artigos vigentes e relações)
    GET  /api/saude            -> status e totais carregados

Regras do chatbot:
    - só usa leis vigentes (vigente / vigente_com_alteracoes) e artigos NÃO revogados (redação vigente);
    - toda resposta cita lei, artigo e link da Câmara;
    - leis revogadas sobre o assunto aparecem em "ignoradas", com a lei que as substituiu.

Rodar:
    pip install fastapi uvicorn
    uvicorn api:app --port 8000
"""
import json
import math
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

VIGENTES = {"vigente", "vigente_com_alteracoes"}
POR_PAGINA = 20

STOPWORDS = set("""
a o as os um uma uns umas de da do das dos em no na nos nas ao aos à às e é ou que se por para pra pro com sem
sobre como qual quais quando onde quem eu meu minha meus minhas seu sua isso esse essa este esta ser ter tem
posso pode podem preciso devo deve existe existem há lei leis municipal municipio município londrina regra regras
artigo artigos fala diz dizer sei saber quero queria gostaria me mim nao não sim mais menos muito muita
""".split())


def normalizar(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", s)


def radicais(texto):
    """Radical simples: as 5 primeiras letras ("ambiental"/"ambiente" -> "ambie"; "árvores" -> "arvor")."""
    return [t[:5] if len(t) > 5 else t for t in normalizar(texto) if t not in STOPWORDS and len(t) > 2]


def carregar():
    if Path("leis.json").exists():
        return json.load(open("leis.json", encoding="utf-8"))
    with zipfile.ZipFile("leis.zip") as z:
        return json.loads(z.read("leis.json"))


# ---------------- índice em memória ----------------
LEIS = carregar()
POR_ID = {l["id"]: l for l in LEIS}
ARTIGOS = []                       # (lei, artigo) só de leis vigentes e artigos não revogados
IDX_ARTIGO = defaultdict(set)      # radical -> índices em ARTIGOS
IDX_EMENTA = defaultdict(set)      # radical -> ids de leis (todas, inclusive revogadas)
for lei in LEIS:
    for r in set(radicais((lei.get("ementa") or "") + " " + lei["titulo"])):
        IDX_EMENTA[r].add(lei["id"])
    if lei["situacao"] not in VIGENTES:
        continue
    for art in lei["artigos"]:
        if art.get("revogado") or not art["texto"].strip():
            continue
        i = len(ARTIGOS)
        ARTIGOS.append((lei, art))
        for r in set(radicais(art["texto"])):
            IDX_ARTIGO[r].add(i)
N_ART, N_LEI = max(len(ARTIGOS), 1), max(len(LEIS), 1)


def idf(df, n):
    return math.log(1 + n / (1 + df))


def ano_lei(l):
    return int(l["ano"]) if (l.get("ano") or "").isdigit() else 0


# ---------------- formatação no contrato do front ----------------
def resumo(l):
    return {"id": l["id"], "chave": l["chave"], "ano": l["ano"], "data_lei": l["data_lei"], "titulo": l["titulo"],
            "ementa": l.get("ementa") or "", "situacao": l["situacao"], "link": l["link"]}


def numero_legivel(l):
    n = l["chave"] or ""
    return (f"{int(n):,}".replace(",", ".") if n.isdigit() else n) + f"/{l['ano']}"


def substituta(l):
    """Lei que revogou esta (primeira relação revogada_por com id na base)."""
    for r in l.get("relacoes", []):
        if r["tipo"] == "revogada_por" and r["id"] in POR_ID:
            return POR_ID[r["id"]]
    return None


# ---------------- busca ----------------
def pontuar(pergunta):
    rads = list(dict.fromkeys(radicais(pergunta)))
    pts_ementa, pts_art = Counter(), Counter()
    for r in rads:
        if r in IDX_EMENTA:
            w = idf(len(IDX_EMENTA[r]), N_LEI)
            for lid in IDX_EMENTA[r]:
                pts_ementa[lid] += w
        if r in IDX_ARTIGO:
            w = idf(len(IDX_ARTIGO[r]), N_ART)
            for i in IDX_ARTIGO[r]:
                pts_art[i] += w
    return rads, pts_ementa, pts_art


def buscar_fontes(pergunta, max_leis=4, por_lei=2):
    rads, pts_ementa, pts_art = pontuar(pergunta)
    if not rads:
        return [], []
    # pontuação da lei = ementa (peso maior) + melhor artigo; leve preferência por leis mais novas
    melhor_art = defaultdict(list)
    for i, p in pts_art.items():
        melhor_art[ARTIGOS[i][0]["id"]].append((p, i))
    pts_lei = Counter()
    for lid in set(pts_ementa) | set(melhor_art):
        l = POR_ID[lid]
        if l["situacao"] not in VIGENTES:
            continue
        top = max((p for p, _ in melhor_art.get(lid, [])), default=0)
        pts_lei[lid] = 2.0 * pts_ementa.get(lid, 0) + top + ano_lei(l) / 10000
    leis_top = [lid for lid, _ in pts_lei.most_common(max_leis)]

    fontes = []
    for lid in leis_top:
        l = POR_ID[lid]
        arts = sorted(melhor_art.get(lid, []), reverse=True)[:por_lei]
        escolhidos = [ARTIGOS[i][1] for _, i in arts] or [a for a in l["artigos"] if not a.get("revogado") and a["texto"]][:1]
        for a in escolhidos:
            fontes.append({"lei_id": l["id"], "chave": l["chave"], "ano": l["ano"], "ementa": l.get("ementa") or "",
                           "situacao": l["situacao"], "artigo": a["artigo"], "trecho": a["texto"][:700], "link": l["link"]})

    # leis revogadas sobre o mesmo assunto: avisar que foram deixadas de fora
    ignoradas = []
    if leis_top:
        corte = 0.6 * max(pts_ementa.get(leis_top[0], 0), 0.01)
        for lid, p in pts_ementa.most_common(200):
            l = POR_ID[lid]
            if l["situacao"] == "revogada" and p >= corte:
                s = substituta(l)
                motivo = (f"Revogada pela Lei nº {numero_legivel(s)}" if s
                          else (l.get("revogacao_nota") or "Revogada").strip("() "))
                ignoradas.append({"lei_id": l["id"], "chave": l["chave"], "ano": l["ano"], "motivo": motivo,
                                  "revogada_por_id": s["id"] if s else None})
            if len(ignoradas) >= 3:
                break
    return fontes, ignoradas


def montar_resposta(pergunta):
    fontes, ignoradas = buscar_fontes(pergunta)
    if not fontes:
        return {"resposta": "Não encontrei uma lei municipal vigente sobre esse assunto. Tente descrever com outras "
                            "palavras (por exemplo: \"poda de árvore\", \"descarte de lixo\", \"alvará de funcionamento\").",
                "fontes": [], "ignoradas": ignoradas}
    principal = POR_ID[fontes[0]["lei_id"]]
    leis = list(dict.fromkeys(f["lei_id"] for f in fontes))
    partes = [f"A lei vigente mais relevante para a sua pergunta é a **Lei nº {numero_legivel(principal)}**: "
              f"{(principal.get('ementa') or principal['titulo']).rstrip('.')}."]
    trecho = fontes[0]["trecho"].replace("\n", " ")
    partes.append(f"O que diz o {fontes[0]['artigo']}: \"{trecho[:400]}{'…' if len(trecho) > 400 else ''}\"")
    if principal["situacao"] == "vigente_com_alteracoes":
        partes.append("Atenção: esta lei já foi alterada; o texto mostrado é a redação vigente.")
    if len(leis) > 1:
        outras = ", ".join(f"Lei nº {numero_legivel(POR_ID[i])}" for i in leis[1:])
        partes.append(f"Também tratam do assunto: {outras}.")
    for ig in ignoradas[:2]:
        partes.append(f"A Lei nº {numero_legivel(POR_ID[ig['lei_id']])} também tratava disso, mas não vale mais "
                      f"({ig['motivo'][0].lower() + ig['motivo'][1:]}).")
    partes.append("Confira sempre o texto oficial no link da Câmara. Esta resposta não substitui orientação jurídica.")
    return {"resposta": "\n\n".join(partes), "fontes": fontes, "ignoradas": ignoradas}


# ---------------- API ----------------
app = FastAPI(title="Assistente de Leis de Londrina")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Pergunta(BaseModel):
    pergunta: str


@app.post("/api/perguntar")
def perguntar(p: Pergunta):
    return montar_resposta(p.pergunta)


@app.get("/api/leis")
def listar(q: str = "", pagina: int = 1, numero: str | None = None, ano: str | None = None, situacao: str | None = None):
    if numero:
        itens = [l for l in LEIS if l["chave"] == numero.replace(".", "") and (not ano or l["ano"] == ano)]
    elif q.strip():
        _, pts_ementa, _ = pontuar(q)
        itens = [POR_ID[lid] for lid, _ in sorted(pts_ementa.items(), key=lambda x: (-x[1], -ano_lei(POR_ID[x[0]])))]
    else:
        itens = sorted(LEIS, key=ano_lei, reverse=True)
    if situacao:
        itens = [l for l in itens if l["situacao"] == situacao]
    ini = (max(pagina, 1) - 1) * POR_PAGINA
    return {"total": len(itens), "pagina": pagina, "itens": [resumo(l) for l in itens[ini:ini + POR_PAGINA]]}


@app.get("/api/leis/{lei_id}")
def obter(lei_id: str):
    l = POR_ID.get(lei_id)
    if not l:
        raise HTTPException(404, "Lei não encontrada")
    vigentes = [a for a in l["artigos"] if not a.get("revogado") and a["texto"]]
    revogados = [a for a in l["artigos"] if a.get("revogado")]
    return {**resumo(l), "relacoes": l["relacoes"],
            "artigos": [{"ordem": a["ordem"], "artigo": a["artigo"], "texto": a["texto"]} for a in vigentes],
            "artigos_revogados": [{"ordem": a["ordem"], "artigo": a["artigo"], "texto": a["texto_riscado"]} for a in revogados]}


@app.get("/api/saude")
def saude():
    return {"ok": True, "leis": len(LEIS), "artigos_vigentes_indexados": len(ARTIGOS)}
