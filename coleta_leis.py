"""Coleta as leis municipais de Londrina pela API da CML e salva em leis.json.

Uso:
    python coleta_leis.py --paginas 2 --texto   # teste: 100 leis com texto
    python coleta_leis.py                        # lista completa, só ementas
    python coleta_leis.py --texto                # tudo com texto (horas; retoma de onde parou)
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("CML_TOKEN")
API = "https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (hackathon-smartcities-londrina)"}
PAUSA = 0.5
CACHE = Path("cache_textos")

MESES = {
    "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
    "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
}

RE_TITULO = re.compile(
    r"LEI\s+(COMPLEMENTAR\s+)?N\.?\s*[º°o]?\s*([\d\.]+),?\s+DE\s+(\d{1,2})[º°o]?\s+DE\s+(\w+)\s+DE\s+(\d{4})", re.I)
RE_REF_LEI = re.compile(r"Lei\s+(Complementar\s+)?(?:Municipal\s+)?n[º°o\.]*\s*([\d\.]*\d)", re.I)
RE_VERBO_ALTERA = re.compile(
    r"^\s*(Altera|Introduz altera|Insere|Acrescenta|D[áa] nova reda|Modifica|Inclui .* na Lei|Revoga)", re.I)
RE_REVOGA = re.compile(r"revoga(?:m|das?|dos?)?\b(.{0,400})", re.I | re.S)
RE_ARTIGO = re.compile(r"(?m)^\s*(Art\.\s*\d+[º°o]?[A-Z\-]*\.?)")


def limpar(s):
    return re.sub(r"[ \t]+", " ", s.replace("\xa0", " "))


def chave(numero, complementar=False):
    """Identificador único: '14294' para lei ordinária, 'LC-12' para complementar."""
    numero = numero.replace(".", "").strip()
    return f"LC-{numero}" if complementar else numero


def refs_leis(trecho):
    return {chave(num, bool(comp)) for comp, num in RE_REF_LEI.findall(trecho)}


# ---------- API ----------

def chamar_api(call, **params):
    r = requests.get(API, params={"keysoft": TOKEN, "call": call, **params}, headers=HEADERS, timeout=60)
    if r.status_code == 406:
        raise SystemExit("O site respondeu 406 (bloqueio do firewall). Rode a partir de outra rede "
                         "ou peça liberação/contato à CML.")
    r.raise_for_status()
    return r.json()


def listar_leis(tipo="Leis", max_paginas=None):
    pagina, leis = 1, []
    while True:
        dados = chamar_api("legislacoes", tipo=tipo, pagina=pagina)
        if not dados:
            break
        leis.extend(dados)
        print(f"página {pagina}: {len(dados)} leis (total {len(leis)})")
        if max_paginas and pagina >= max_paginas:
            break
        pagina += 1
        time.sleep(PAUSA)
    return leis


# ---------- parsing ----------

def parse_titulo(titulo):
    m = RE_TITULO.search(limpar(titulo))
    if not m:
        return None, None, False
    complementar, num, dia, mes, ano = m.groups()
    mes_n = MESES.get(mes.upper())
    data = f"{ano}-{mes_n:02d}-{int(dia):02d}" if mes_n else None
    return num.replace(".", ""), data, bool(complementar)


def limpar_ementa(ementa):
    return re.sub(r"^\s*S[ÚU]MULA:\s*", "", limpar(ementa), flags=re.I).strip()


def altera_pela_ementa(ementa):
    if not RE_VERBO_ALTERA.search(ementa):
        return []
    return sorted(refs_leis(ementa))


def extrair_texto(html):
    texto = limpar(BeautifulSoup(html, "html.parser").get_text("\n"))
    inicio = texto.find("pasta digital")
    if inicio != -1:
        texto = texto[inicio + len("pasta digital"):]
    fim = texto.find("Protocolos desta Publicação")
    if fim != -1:
        texto = texto[:fim]
    return "\n".join(l.strip() for l in texto.splitlines() if l.strip())


def baixar_texto(id_, link):
    """Baixa o texto da lei, usando cache em disco para poder retomar."""
    arq = CACHE / f"{id_}.txt"
    if arq.exists():
        return arq.read_text(encoding="utf-8")
    r = requests.get(link, headers=HEADERS, timeout=60)
    r.raise_for_status()
    texto = extrair_texto(r.text)
    CACHE.mkdir(exist_ok=True)
    arq.write_text(texto, encoding="utf-8")
    time.sleep(PAUSA)
    return texto


def separar_artigos(texto):
    partes = RE_ARTIGO.split(texto)
    artigos = []
    for i in range(1, len(partes), 2):
        rotulo = re.sub(r"\s+", " ", partes[i]).strip().rstrip(".")
        corpo = partes[i + 1] if i + 1 < len(partes) else ""
        artigos.append({"artigo": rotulo, "texto": (partes[i] + corpo).strip()})
    return artigos


def revoga_pelo_texto(texto):
    chaves = set()
    for trecho in RE_REVOGA.findall(texto):
        trecho = re.split(r"\n(?=Art\.)|\.\s*\n", trecho)[0]
        chaves |= refs_leis(trecho)
    return sorted(chaves)


# ---------- montagem ----------

def montar_registro(item, com_texto):
    numero, data_lei, complementar = parse_titulo(item["titulo"])
    ementa = limpar_ementa(item["ementa"])
    link = item["link"].split("#")[0]
    id_ = link.rstrip("/").split("/")[-1]
    minha_chave = chave(numero, complementar) if numero else None
    registro = {
        "id": id_,
        "chave": minha_chave,
        "tipo": "Lei Complementar" if complementar else "Lei",
        "numero": numero,
        "data_lei": data_lei,
        "ano": data_lei[:4] if data_lei else None,
        "titulo": limpar(item["titulo"]).strip(),
        "ementa": ementa,
        "publicado_site": item["data"],
        "link": link,
        "altera": [c for c in altera_pela_ementa(ementa) if c != minha_chave],
        "revoga": [],
        "situacao": "vigente",
        "revogada_por": [],
        "alterada_por": [],
        "artigos": [],
    }
    if com_texto:
        try:
            texto = baixar_texto(id_, link)
            registro["artigos"] = separar_artigos(texto)
            registro["revoga"] = [c for c in revoga_pelo_texto(texto) if c != minha_chave]
        except requests.RequestException as e:
            registro["erro_texto"] = str(e)
    return registro


def calcular_vigencia(leis):
    por_chave = {l["chave"]: l for l in leis if l["chave"]}
    for lei in leis:
        for c in lei["revoga"]:
            alvo = por_chave.get(c)
            if alvo:
                alvo["situacao"] = "revogada"
                alvo["revogada_por"].append(lei["chave"])
        for c in lei["altera"]:
            alvo = por_chave.get(c)
            if alvo:
                alvo["alterada_por"].append(lei["chave"])
    for lei in leis:
        if lei["situacao"] == "vigente" and lei["alterada_por"]:
            lei["situacao"] = "vigente_com_alteracoes"
    return leis


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paginas", type=int, help="máximo de páginas da API (50 leis cada)")
    ap.add_argument("--texto", action="store_true", help="baixa também o texto de cada lei")
    ap.add_argument("--saida", default="leis.json")
    args = ap.parse_args()
    if not TOKEN:
        raise SystemExit("Defina CML_TOKEN no arquivo .env")

    brutos = listar_leis(max_paginas=args.paginas)
    leis = []
    for i, item in enumerate(brutos, 1):
        leis.append(montar_registro(item, args.texto))
        if args.texto and i % 50 == 0:
            print(f"textos: {i}/{len(brutos)}")
    leis = calcular_vigencia(leis)

    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)
    resumo = {s: sum(l["situacao"] == s for l in leis) for s in ("vigente", "vigente_com_alteracoes", "revogada")}
    print(f"{len(leis)} leis salvas em {args.saida} -> {resumo}")


if __name__ == "__main__":
    main()
