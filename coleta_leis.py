"""Coleta as leis municipais de Londrina pela API da CML e salva em leis.json.

Uso:
    python coleta_leis.py --paginas 2 --texto   # teste: 100 leis com texto
    python coleta_leis.py                        # lista completa, só ementas (~5 min)
    python coleta_leis.py --texto                # tudo com texto e relacionamentos (retoma de onde parou)
"""
import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
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

# "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026" ou "LEI ORDINÁRIA Nº 11341/2011"
RE_NUMERO = re.compile(r"\bN[\.º°o\s]*\s*(\d[\d\.]*\d|\d)(?:\s*-?\s*([A-Z])\b)?", re.I)
RE_DATA_EXTENSO = re.compile(r"\bDE\s+(\d{1,2})\s*[º°o]?\s+DE\s+([A-ZÇa-zç]+)\s+DE\s+(\d{4})", re.I)
RE_ANO_BARRA = re.compile(r"/\s*(\d{4})\b")
RE_REF_LEI = re.compile(r"Lei\s+(Complementar\s+)?(?:Municipal\s+)?(?:n[º°o\.]*\s*)?(\d[\d\.]*\d|\d)", re.I)
RE_VERBO_ALTERA = re.compile(
    r"^\s*(Altera|Introduz altera|Insere|Acrescenta|D[áa] nova reda|Modifica|Inclui .* na Lei|Revoga)", re.I)
# Anotação oficial da CML na ementa de lei revogada por inteiro:
# "(REVOGADA pelo art. 270. da Lei nº 12.236, de 29 de janeiro de 2015)"
RE_ANOTACAO_REVOGADA = re.compile(r"\(\s*REVOGAD[AO]\b([^()]*)\)", re.I)
RE_ARTIGO = re.compile(r"(?m)^\s*(Art\.\s*\d+[º°o]?[A-Z\-]*\.?)")

# Rótulos da seção "Relacionamentos desta Matéria" que interessam
RELACOES = {
    "Altera": "altera", "Alterada por": "alterada_por",
    "Revoga": "revoga", "Revogada por": "revogada_por",
    "Cita": "cita", "Citada por": "citada_por",
}


def limpar(s):
    return re.sub(r"[ \t]+", " ", s.replace("\xa0", " "))


def chave(numero, complementar=False):
    """Identificador legível: '14294' para lei ordinária, 'LC-12' para complementar."""
    numero = numero.replace(".", "").strip()
    return f"LC-{numero}" if complementar else numero


def refs_leis(trecho):
    return {chave(num, bool(comp)) for comp, num in RE_REF_LEI.findall(trecho)}


def parse_data(texto):
    m = RE_DATA_EXTENSO.search(texto)
    if not m:
        return None
    dia, mes, ano = m.groups()
    mes_n = MESES.get(mes.upper())
    return f"{ano}-{mes_n:02d}-{int(dia):02d}" if mes_n else None


# ---------- API ----------

def baixar(url, tentativas=5, **kwargs):
    """GET com novas tentativas e espera crescente (5s, 10s, 20s, 40s) em caso de falha de rede."""
    for n in range(tentativas):
        try:
            r = requests.get(url, headers=HEADERS, timeout=90, **kwargs)
            if r.status_code == 406:
                raise SystemExit("O site respondeu 406 (bloqueio do firewall). Rode a partir de outra rede "
                                 "ou peça liberação à CML.")
            if r.status_code < 500:
                r.raise_for_status()
                return r
            erro = requests.HTTPError(f"HTTP {r.status_code}")
        except (requests.ConnectionError, requests.Timeout) as e:
            erro = e
        if n < tentativas - 1:
            espera = 5 * 2 ** n
            print(f"falha em {url[:80]} ({type(erro).__name__}); nova tentativa em {espera}s", flush=True)
            time.sleep(espera)
    raise erro


def chamar_api(call, **params):
    return baixar(API, params={"keysoft": TOKEN, "call": call, **params}).json()


def listar_leis(tipo="Leis", max_paginas=None):
    pagina, leis, vistos = 1, [], set()
    while True:
        dados = chamar_api("legislacoes", tipo=tipo, pagina=pagina)
        if not dados:
            break
        for item in dados:  # se uma lei nova for publicada durante a coleta, as páginas "andam"
            if item["link"] not in vistos:
                vistos.add(item["link"])
                leis.append(item)
        print(f"página {pagina}: {len(dados)} leis (total {len(leis)})", flush=True)
        if max_paginas and pagina >= max_paginas:
            break
        pagina += 1
        time.sleep(PAUSA)
    return leis


# ---------- parsing ----------

def parse_titulo(titulo):
    """Retorna (numero, data_lei, ano, complementar)."""
    titulo = limpar(titulo)
    m = RE_NUMERO.search(titulo)
    numero = None
    if m:
        numero = m.group(1).replace(".", "") + (f"-{m.group(2).upper()}" if m.group(2) else "")
    data = parse_data(titulo)
    if data:
        ano = data[:4]
    else:
        a = RE_ANO_BARRA.search(titulo)
        ano = a.group(1) if a else None
    return numero, data, ano, "COMPLEMENTAR" in titulo.upper()


def limpar_ementa(ementa):
    return re.sub(r"^\s*S[ÚU]MULA:\s*", "", limpar(ementa), flags=re.I).strip()


def revogacao_na_ementa(ementa):
    """Se a CML anotou a lei como revogada, devolve as chaves de quem revogou ([] se nenhuma citada).
    Devolve None se não há anotação."""
    m = RE_ANOTACAO_REVOGADA.search(ementa)
    if not m:
        return None
    return sorted(refs_leis(m.group(1)))


def altera_pela_ementa(ementa):
    ementa = RE_ANOTACAO_REVOGADA.sub("", ementa)
    if not RE_VERBO_ALTERA.search(ementa):
        return []
    return sorted(refs_leis(ementa))


def extrair_texto(soup):
    texto = limpar(soup.get_text("\n"))
    inicio = texto.find("pasta digital")
    if inicio != -1:
        texto = texto[inicio + len("pasta digital"):]
    fim = texto.find("Protocolos desta Publicação")
    if fim != -1:
        texto = texto[:fim]
    return "\n".join(l.strip() for l in texto.splitlines() if l.strip())


def extrair_relacionamentos(soup):
    """Lê a seção oficial 'Relacionamentos desta Matéria' da página da lei."""
    rels = []
    for a in soup.select("#menu_opcao_proposicao_relacionamentos a.menu-opcoes__items"):
        forte = a.find("strong")
        if not forte:
            continue
        cabecalho = forte.get_text(" ", strip=True)  # "05/01/2012 00:00 - Revoga:"
        tipo = cabecalho.split(" - ", 1)[-1].rstrip(":").strip()
        rels.append({
            "tipo": tipo,
            "id": a.get("href", "").rstrip("/").split("/")[-1],
            "descricao": limpar(a.get_text(" ", strip=True)[len(cabecalho):]).strip(),
        })
    return rels


def baixar_pagina(id_, link):
    """Baixa texto e relacionamentos da lei, com cache em disco para poder retomar."""
    arq = CACHE / f"{id_}.json"
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    r = baixar(link)
    soup = BeautifulSoup(r.text, "html.parser")
    dados = {"texto": extrair_texto(soup), "relacionamentos": extrair_relacionamentos(soup)}
    CACHE.mkdir(exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    time.sleep(PAUSA)
    return dados


def separar_artigos(texto):
    partes = RE_ARTIGO.split(texto)
    artigos = []
    for i in range(1, len(partes), 2):
        rotulo = re.sub(r"\s+", " ", partes[i]).strip().rstrip(".")
        corpo = partes[i + 1] if i + 1 < len(partes) else ""
        artigos.append({"ordem": len(artigos) + 1, "artigo": rotulo, "texto": (partes[i] + corpo).strip()})
    return artigos


# ---------- montagem ----------

def montar_registro(item):
    numero, data_lei, ano, complementar = parse_titulo(item["titulo"])
    ementa = limpar_ementa(item["ementa"])
    link = item["link"].split("#")[0]
    minha_chave = chave(numero, complementar) if numero else None
    revogada = revogacao_na_ementa(ementa)
    return {
        "id": link.rstrip("/").split("/")[-1],
        "chave": minha_chave,
        "tipo": "Lei Complementar" if complementar else "Lei",
        "numero": numero,
        "data_lei": data_lei,
        "ano": ano,
        "titulo": limpar(item["titulo"]).strip(),
        "ementa": ementa,
        "publicado_site": item["data"],
        "link": link,
        "situacao": "revogada" if revogada is not None else "vigente",
        "altera": [c for c in altera_pela_ementa(ementa) if c != minha_chave],
        "alterada_por": [],
        "revoga": [],
        "revogada_por": revogada or [],
        "fonte_relacoes": "ementa",
        "relacionamentos": [],
        "artigos": [],
    }


def adicionar_texto(registro):
    try:
        dados = baixar_pagina(registro["id"], registro["link"])
    except requests.RequestException as e:
        registro["erro_texto"] = str(e)
        return registro
    registro["artigos"] = separar_artigos(dados["texto"])
    registro["relacionamentos"] = dados["relacionamentos"]
    registro["fonte_relacoes"] = "cml"
    if not registro["data_lei"]:
        registro["data_lei"] = parse_data(dados["texto"][:800])
    return registro


CAMPOS_RELACAO = ("altera", "alterada_por", "revoga", "revogada_por")


def resolver_id(c, lei, por_chave, alvo_mais_novo):
    """Acha o id da lei citada pelo número. Quando o número se repete (ex.: duas Leis nº 48 de 1949),
    escolhe pela data: quem altera ou revoga é mais nova do que a lei alterada ou revogada."""
    candidatas = por_chave.get(c, [])
    if len(candidatas) > 1 and lei["ano"]:
        if alvo_mais_novo:
            filtradas = sorted((x for x in candidatas if (x["ano"] or "") >= lei["ano"]), key=lambda x: x["ano"])
        else:
            filtradas = sorted((x for x in candidatas if (x["ano"] or "9999") <= lei["ano"]), key=lambda x: x["ano"])[::-1]
        candidatas = filtradas or candidatas
    return candidatas[0]["id"] if candidatas else None


def adicionar_relacao(lei, tipo, id_, c):
    for r in lei["relacoes"]:
        if r["tipo"] == tipo and ((id_ and r["id"] == id_) or (not id_ and r["chave"] == c)):
            return
    lei["relacoes"].append({"tipo": tipo, "id": id_, "chave": c})


def calcular_vigencia(leis):
    """Monta lei["relacoes"] (lista de {tipo, id, chave}; id é None se a lei citada não está no arquivo),
    preenche as listas de chaves altera/alterada_por/revoga/revogada_por e define a situação."""
    por_id = {l["id"]: l for l in leis}
    por_chave = {}
    for l in leis:
        if l["chave"]:
            por_chave.setdefault(l["chave"], []).append(l)

    deduzidas = {l["id"]: {"altera": l["altera"], "revogada_por": l["revogada_por"]} for l in leis}
    for l in leis:
        l["relacoes"] = []

    for lei in leis:
        # Revogação total anotada na ementa (vale para qualquer fonte)
        for c in deduzidas[lei["id"]]["revogada_por"]:
            adicionar_relacao(lei, "revogada_por", resolver_id(c, lei, por_chave, True), c)

        if lei["fonte_relacoes"] == "cml":
            # Relações oficiais da seção "Relacionamentos desta Matéria"
            for rel in lei["relacionamentos"]:
                tipo = RELACOES.get(rel["tipo"])
                if tipo not in CAMPOS_RELACAO:
                    continue
                alvo = por_id.get(rel["id"])
                if alvo:
                    adicionar_relacao(lei, tipo, alvo["id"], alvo["chave"])
                elif rel["descricao"].upper().startswith("LEI"):  # lei fora do arquivo
                    numero, _, _, complementar = parse_titulo(rel["descricao"][:80])
                    if numero:
                        adicionar_relacao(lei, tipo, None, chave(numero, complementar))
        else:
            # Sem texto: alterações deduzidas da ementa
            for c in deduzidas[lei["id"]]["altera"]:
                adicionar_relacao(lei, "altera", resolver_id(c, lei, por_chave, False), c)

    # Completa o lado inverso nas leis que não têm as relações oficiais
    inverso = {"altera": "alterada_por", "revogada_por": "revoga"}
    for lei in leis:
        for r in list(lei["relacoes"]):
            alvo = por_id.get(r["id"]) if r["id"] else None
            if r["tipo"] in inverso and alvo and alvo["fonte_relacoes"] != "cml":
                adicionar_relacao(alvo, inverso[r["tipo"]], lei["id"], lei["chave"])

    for lei in leis:
        for campo in CAMPOS_RELACAO:
            lei[campo] = list(dict.fromkeys(r["chave"] for r in lei["relacoes"] if r["tipo"] == campo and r["chave"]))
        # "Revogada por" sem a anotação de REVOGADA na ementa = revogação parcial (só alguns dispositivos)
        if lei["situacao"] == "vigente" and (lei["alterada_por"] or lei["revogada_por"]):
            lei["situacao"] = "vigente_com_alteracoes"
    return leis


def main():
    global PAUSA
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paginas", type=int, help="máximo de páginas da API (50 leis cada)")
    ap.add_argument("--texto", action="store_true", help="baixa texto e relacionamentos de cada lei")
    ap.add_argument("--paralelo", type=int, default=3, help="downloads simultâneos de texto (padrão 3)")
    ap.add_argument("--saida", default="leis.json")
    args = ap.parse_args()
    if not TOKEN:
        raise SystemExit("Defina CML_TOKEN no arquivo .env")

    leis = [montar_registro(item) for item in listar_leis(max_paginas=args.paginas)]
    if args.texto:
        with ThreadPoolExecutor(max_workers=args.paralelo) as pool:
            for i, _ in enumerate(pool.map(adicionar_texto, leis), 1):
                if i % 100 == 0:
                    print(f"textos: {i}/{len(leis)}", flush=True)
    leis = calcular_vigencia(leis)

    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)
    resumo = {s: sum(l["situacao"] == s for l in leis) for s in ("vigente", "vigente_com_alteracoes", "revogada")}
    erros = sum("erro_texto" in l for l in leis)
    print(f"{len(leis)} leis salvas em {args.saida} -> {resumo}" + (f" ({erros} sem texto)" if erros else ""))


if __name__ == "__main__":
    main()
