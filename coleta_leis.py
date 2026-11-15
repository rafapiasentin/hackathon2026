"""Coleta as leis municipais de Londrina pela API da CML e salva em leis.json.

Uso:
    python coleta_leis.py --paginas 2 --texto   # teste: 100 leis com texto
    python coleta_leis.py                        # lista completa, só ementas (~5 min)
    python coleta_leis.py --texto                # tudo com texto e relacionamentos (retoma de onde parou)

Explicação detalhada, passo a passo: docs/COMO_FUNCIONA.md

VISÃO GERAL DO FLUXO
--------------------
    API da Câmara ──► lista das leis (número, título, ementa, link)          [ETAPA 1]
            │
            ▼
    título e ementa ──► número, data, ano, "(REVOGADA pelo ...)"             [ETAPA 2]
            │
            ▼
    página de cada lei ──► texto completo + "Relacionamentos desta Matéria"  [ETAPA 3]
            │
            ▼
    tratamento do texto ──► rodapé removido, data da lei, artigos            [ETAPA 4]
            │
            ▼
    ligação entre as leis ──► quem altera/revoga quem + situação             [ETAPA 5]
            │
            ▼
    leis.json                                                                [ETAPA 6: main]
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests                      # faz as requisições HTTP (baixa páginas, chama a API)
from bs4 import BeautifulSoup        # lê o HTML das páginas e permite buscar partes dele
from dotenv import load_dotenv       # lê o arquivo .env com o token

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

load_dotenv()  # carrega as variáveis do arquivo .env (que NÃO vai para o git)

TOKEN = os.getenv("CML_TOKEN")  # token da API da Câmara (parâmetro "keysoft")
API = "https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (hackathon-smartcities-londrina)"}
PAUSA = 0.5                     # segundos de espera entre requisições, para não sobrecarregar o site
CACHE = Path("cache_textos")    # cada lei baixada fica salva aqui como <id>.json (permite retomar)
# Versão do formato do cache. Se mudar o que é extraído da página (ex.: passar a marcar o texto riscado),
# aumente este número: arquivos de cache com versão antiga são baixados de novo.
VERSAO_CACHE = 2
# Versão do formato do leis.json (registrada no leis.meta.json)
VERSAO_FORMATO = "2.0"

# Converte o mês por extenso do título/assinatura em número ("OUTUBRO" -> 10)
MESES = {
    "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
    "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
}

# =============================================================================
# EXPRESSÕES REGULARES (regex)
# Uma regex é um "padrão" de texto. re.I = ignora maiúsculas/minúsculas.
# Os parênteses (...) são GRUPOS: o pedaço que queremos capturar.
# (?:...) é um grupo que NÃO captura (só agrupa). "?" depois de algo = opcional.
# =============================================================================

# Número da lei no título. Os títulos vêm em dois formatos:
#   "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026"   (leis recentes, ~420)
#   "LEI ORDINÁRIA Nº 11341/2011"               (leis antigas, ~13.900)
#   "LEI N.º 520 - A, DE 8 DE DEZEMBRO DE 1959" (algumas têm letra)
#   \bN[\.º°o\s]*          -> "N", "Nº", "N.º", "No"
#   (\d[\d\.]*\d|\d)       -> grupo 1: o número, que pode ter ponto ("13.939")
#   (?:\s*-?\s*([A-Z])\b)? -> grupo 2 (opcional): a letra (" - A", "- A", " A")
RE_NUMERO = re.compile(r"\bN[\.º°o\s]*\s*(\d[\d\.]*\d|\d)(?:\s*-?\s*([A-Z])\b)?", re.I)

# Data por extenso: "DE 29 DE OUTUBRO DE 2026" -> grupos (dia, mês, ano). Aceita "1º".
RE_DATA_EXTENSO = re.compile(r"\bDE\s+(\d{1,2})\s*[º°o]?\s+DE\s+([A-ZÇa-zç]+)\s+DE\s+(\d{4})", re.I)

# Ano depois da barra no formato antigo: "Nº 11341/2011" -> "2011"
RE_ANO_BARRA = re.compile(r"/\s*(\d{4})\b")

# Menção a uma lei dentro de um texto: "Lei nº 14.294", "Lei Municipal nº 11.054",
# "Lei 13.106" (sem "nº"), "Lei Complementar nº 12".
#   grupo 1: "Complementar " (se existir)   grupo 2: o número
RE_REF_LEI = re.compile(r"Lei\s+(Complementar\s+)?(?:Municipal\s+)?(?:n[º°o\.]*\s*)?(\d[\d\.]*\d|\d)", re.I)

# Ementa que COMEÇA (^) com um verbo de alteração: "Altera a Lei nº ...", "Insere artigo..."
# Usada só quando não temos as relações oficiais (coleta sem --texto).
RE_VERBO_ALTERA = re.compile(
    r"^\s*(Altera|Introduz altera|Insere|Acrescenta|D[áa] nova reda|Modifica|Inclui .* na Lei|Revoga)", re.I)

# Anotação oficial da CML na ementa de lei revogada por inteiro:
# "(REVOGADA pelo art. 270. da Lei nº 12.236, de 29 de janeiro de 2015)"
#   \(\s*REVOGAD[AO]\b -> abre parêntese + "REVOGADA" ou "REVOGADO"
#   (?=...)             -> só vale se citar uma LEI ou não citar DECRETO nenhum (ver abaixo)
#   ([^()]*)            -> grupo 1: tudo até fechar o parêntese (onde está a lei revogadora)
# Decreto não revoga lei. Uma anotação que cita só decreto fala de OUTRO decreto citado na ementa.
# Ex. (Lei 13.905): "(Vide Decreto nº 413, de 2025) (Revogado pelo Decreto 1.341, de 2026)":
# quem foi revogado é o Decreto 413, e a lei continua valendo.
RE_ANOTACAO_REVOGADA = re.compile(r"\(\s*REVOGAD[AO]\b(?=[^()]*\bLei\b|(?![^()]*\bDecreto\b))([^()]*)\)", re.I)

# Início de artigo: "Art. 1º", "Art. 225.", "Art. 5º-A".
# (?m)^ = só no COMEÇO DE UMA LINHA. Assim "conforme o art. 5º" no meio de uma frase não vira artigo.
# ⟦? = o artigo pode começar riscado (ver MARCAÇÃO DO TEXTO RISCADO abaixo).
RE_ARTIGO = re.compile(r"(?m)^\s*(⟦?Art\.\s*\d+[º°o]?[A-Z\-]*\.?)")

# MARCAÇÃO DO TEXTO RISCADO
# As páginas da Câmara mostram o TEXTO COMPILADO: a redação antiga aparece RISCADA (<strike>, <s>, <del>
# ou estilo "line-through") ao lado da redação nova. Na extração, cada linha riscada vira "⟦...⟧".
# Depois, o texto riscado é separado do texto vigente de cada artigo (separar_artigos).
RE_RISCADO = re.compile(r"⟦[^⟧]*⟧")
RE_LINE_THROUGH = re.compile(r"line-through", re.I)

# Súmula dentro do texto (usada quando a API devolve a ementa vazia):
# "SÚMULA:\nDesafeta de uso comum ...\nA CÂMARA MUNICIPAL DE LONDRINA..." -> "Desafeta de uso comum ..."
RE_SUMULA = re.compile(r"S[ÚU]MULA:\s*(.+?)\s*(?:\n\s*A C[ÂA]MARA MUNICIPAL|\Z)", re.I | re.S)

# Promulgação de partes vetadas: quando a Câmara derruba um veto, publica os trechos à parte, com o
# MESMO número da lei. Ex.: "...EU, PRESIDENTE, PROMULGO, NOS TERMOS DO § 7º DO ARTIGO 31 DA LEI
# ORGÂNICA DO MUNICÍPIO, OS SEGUINTES DISPOSITIVOS DA LEI MUNICIPAL Nº 13960..."
RE_PROMULGACAO_VETO = re.compile(r"PROMULGO,?\s+NOS TERMOS.{0,120}?SEGUINTES DISPOSITIVOS DA LEI", re.I | re.S)

# Assinatura no fim da lei, de onde tiramos a data das leis antigas:
#   "Londrina, 5 de janeiro de 2012."
#   "EDIFÍCIO DA PREFEITURA DO MUNICÍPIO DE LONDRINA, aos 3 de julho de 1970."
#   "Londrina, 14 de novembro de 1.991."   (ano com ponto: \d\.?\d{3})
RE_ASSINATURA = re.compile(r"LONDRINA,?\s*(?:aos|em)?\s*(\d{1,2})\s*[º°o]?\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d\.?\d{3})", re.I)

# Data do anexo em PDF (leis que só têm PDF): linha "Anexos (1)" seguida de "18/10/1994 00:00 -"
RE_ANEXO = re.compile(r"Anexos \(\d+\)\n(\d{2})/(\d{2})/(\d{4})")

# Onde começa o rodapé do site, que aparece no fim do texto das páginas antigas
# ("Observações: As normas e informações complementares... Certidão de Utilidade Pública, Pautas...")
RE_RODAPE = re.compile(r"\n(?:Anexos \(\d+\)\n|Observações:\nAs normas e informações complementares)")

# Rótulos da seção "Relacionamentos desta Matéria" -> nome do campo no leis.json.
# Rótulos fora desta lista (Sanção, Promulgação, Vínculo) ficam só em "relacionamentos" (lista crua).
RELACOES = {
    "Altera": "altera", "Alterada por": "alterada_por",
    "Revoga": "revoga", "Revogada por": "revogada_por",
    "Cita": "cita", "Citada por": "citada_por",
}


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def limpar(s):
    """Troca o espaço especial do site (\\xa0, "non-breaking space") por espaço normal
    e junta espaços repetidos. Ex.: "Lei\\xa0nº   10" -> "Lei nº 10"."""
    return re.sub(r"[ \t]+", " ", s.replace("\xa0", " "))


def chave(numero, complementar=False):
    """Identificador legível da lei: '14294' para lei ordinária, 'LC-12' para complementar.
    Atenção: NÃO é único (existem leis diferentes com o mesmo número). O identificador único é o "id"."""
    numero = numero.replace(".", "").strip()
    return f"LC-{numero}" if complementar else numero


def refs_leis(trecho):
    """Todas as leis citadas num trecho, como chaves.
    Ex.: "Altera a Lei nº 11.054 e a Lei Complementar nº 12" -> {"11054", "LC-12"}"""
    return {chave(num, bool(comp)) for comp, num in RE_REF_LEI.findall(trecho)}


def parse_data(texto):
    """Converte a primeira data por extenso do texto para o formato AAAA-MM-DD.
    Ex.: "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026" -> "2026-10-29". Devolve None se não achar."""
    m = RE_DATA_EXTENSO.search(texto)
    if not m:
        return None
    dia, mes, ano = m.groups()
    mes_n = MESES.get(mes.upper())
    return f"{ano}-{mes_n:02d}-{int(dia):02d}" if mes_n else None


def data_valida(data):
    """True se "AAAA-MM-DD" é uma data que existe no calendário.
    Ex.: "2010-02-29" -> False (2010 não foi bissexto; erro de digitação no texto da Lei 10.887)."""
    try:
        datetime.date.fromisoformat(data)
        return True
    except (TypeError, ValueError):
        return False


def sem_riscado(texto):
    """Remove o texto riscado ("⟦...⟧") e as linhas que ficaram vazias."""
    return "\n".join(l for l in RE_RISCADO.sub("", texto).splitlines() if l.strip())


# =============================================================================
# ETAPA 1 — LISTAR AS LEIS PELA API
# A API devolve 50 leis por página, da mais nova para a mais antiga. Cada item vem assim:
#   {"data": "2026-11-04 18:44:30",            <- quando entrou no SITE (não é a data da lei!)
#    "titulo": "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
#    "ementa": "SÚMULA: Institui o Código Ambiental do Município de Londrina.",
#    "autoria": "",
#    "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902#pesquisa"}
# =============================================================================

def baixar(url, tentativas=5, **kwargs):
    """GET com novas tentativas e espera crescente (5s, 10s, 20s, 40s) em caso de falha de rede.

    Por quê: na primeira coleta completa o site demorou a responder e o script inteiro caiu.
    A espera dobra a cada falha ("backoff exponencial"), dando tempo para o servidor se recuperar.
    - 406: bloqueio do firewall do site -> não adianta tentar de novo, para o script.
    - 5xx: erro do servidor -> tenta de novo.
    - 4xx (ex.: 404): erro "definitivo" -> raise_for_status() lança a exceção na hora.
    """
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
            erro = e  # caiu a conexão ou passou do tempo limite
        if n < tentativas - 1:
            espera = 5 * 2 ** n  # 5, 10, 20, 40 segundos
            print(f"falha em {url[:80]} ({type(erro).__name__}); nova tentativa em {espera}s", flush=True)
            time.sleep(espera)
    raise erro  # falhou todas as tentativas


def chamar_api(call, **params):
    """Chama a API da CML e devolve o JSON já convertido para lista/dicionário Python.
    Ex.: chamar_api("legislacoes", tipo="Leis", pagina=1)"""
    return baixar(API, params={"keysoft": TOKEN, "call": call, **params}).json()


def listar_leis(tipo="Leis", max_paginas=None):
    """Percorre as páginas da API (1, 2, 3...) até vir uma página vazia e devolve todos os itens.

    O conjunto "vistos" evita duplicatas: se a Câmara publicar uma lei nova DURANTE a coleta,
    todas as leis "andam" uma posição e a última da página 5 reaparece na página 6.
    """
    pagina, leis, vistos = 1, [], set()
    while True:
        dados = chamar_api("legislacoes", tipo=tipo, pagina=pagina)
        if not dados:  # página vazia = acabou
            break
        for item in dados:
            if item["link"] not in vistos:
                vistos.add(item["link"])
                leis.append(item)
        print(f"página {pagina}: {len(dados)} leis (total {len(leis)})", flush=True)
        if max_paginas and pagina >= max_paginas:  # --paginas N (para testes)
            break
        pagina += 1
        time.sleep(PAUSA)
    return leis


# =============================================================================
# ETAPA 2 — LER O TÍTULO E A EMENTA
# =============================================================================

def parse_titulo(titulo):
    """Extrai do título: (numero, data_lei, ano, complementar).

    Exemplos:
        "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026"   -> ("14294", "2026-10-29", "2026", False)
        "LEI ORDINÁRIA Nº 11341/2011"               -> ("11341", None, "2011", False)
        "LEI N.º 520 - B, DE 8 DE DEZEMBRO DE 1959" -> ("520-B", "1959-12-08", "1959", False)
    Quando a data é None, ela é procurada depois no texto da lei (ETAPA 4).
    """
    titulo = limpar(titulo)
    m = RE_NUMERO.search(titulo)
    numero = None
    if m:
        # grupo 1 = número sem os pontos; grupo 2 = letra opcional -> "520-B"
        numero = m.group(1).replace(".", "") + (f"-{m.group(2).upper()}" if m.group(2) else "")
    data = parse_data(titulo)
    if data:
        ano = data[:4]
    else:
        a = RE_ANO_BARRA.search(titulo)  # formato antigo: ano depois da barra
        ano = a.group(1) if a else None
    return numero, data, ano, "COMPLEMENTAR" in titulo.upper()


def limpar_ementa(ementa):
    """Tira o prefixo "SÚMULA:" e os espaços estranhos da ementa."""
    return re.sub(r"^\s*S[ÚU]MULA:\s*", "", limpar(ementa), flags=re.I).strip()


def revogacao_na_ementa(ementa):
    """Lê a anotação oficial de revogação TOTAL que a própria Câmara escreve na ementa.

    Ex.: "Institui o Código Ambiental... (REVOGADA pelo Art. 225. da Lei nº 14.294, de 29 de outubro de 2026)"
         -> ["14294"]
    Devolve:
        None -> não há anotação (lei não revogada por inteiro)
        []   -> há anotação, mas sem lei citada (ex.: revogada por decreto, ou erro de digitação)
        [..] -> chaves das leis que revogaram
    """
    m = RE_ANOTACAO_REVOGADA.search(ementa)
    if not m:
        return None
    return sorted(refs_leis(m.group(1)))


def altera_pela_ementa(ementa):
    """PLANO B (coleta sem --texto): deduz quais leis esta lei altera, pela ementa.
    Só considera ementas que COMEÇAM com verbo de alteração.
    Ex.: "Altera a Lei Municipal nº 11.054, de 2010" -> ["11054"]
         "Institui o Código Ambiental"               -> []
    """
    ementa = RE_ANOTACAO_REVOGADA.sub("", ementa)  # tira "(REVOGADA ...)" para não confundir
    if not RE_VERBO_ALTERA.search(ementa):
        return []
    return sorted(refs_leis(ementa))


# =============================================================================
# ETAPA 3 — BAIXAR A PÁGINA DE CADA LEI
# A página (o "link") traz o que a API não traz: o TEXTO COMPLETO e a seção oficial
# "Relacionamentos desta Matéria" (Altera, Alterada por, Revoga, Revogada por...).
# =============================================================================

def marcar_riscado(soup):
    """Troca cada trecho riscado da página por linhas "⟦...⟧" (redação antiga, que não vale mais).

    Ex.: <strike>Art. 3º As obras deverão ser iniciadas dentro do prazo de um ano...</strike>
         vira a linha "⟦Art. 3º As obras deverão ser iniciadas dentro do prazo de um ano...⟧"
    Cada linha é marcada separadamente para que um bloco riscado com vários artigos continue
    sendo separado em artigos. Marcas de riscados aninhados são removidas antes, para não duplicar.
    """
    riscados = soup.select("strike, s, del") + soup.find_all(style=RE_LINE_THROUGH)
    for el in riscados:
        linhas = [l.replace("⟦", "").replace("⟧", "").strip() for l in el.get_text("\n").splitlines()]
        el.replace_with("\n" + "\n".join(f"⟦{l}⟧" for l in linhas if l) + "\n")


def extrair_texto(soup):
    """Pega só o texto da lei de dentro da página inteira.
    O texto começa depois do botão "pasta digital" e termina antes de "Protocolos desta Publicação"
    (nas páginas antigas esse marcador não existe; o rodapé é cortado depois, em processar_texto).
    O texto riscado vem marcado como "⟦...⟧" (ver marcar_riscado)."""
    marcar_riscado(soup)
    texto = limpar(soup.get_text("\n"))  # todo o texto visível, uma linha por elemento
    inicio = texto.find("pasta digital")
    if inicio != -1:
        texto = texto[inicio + len("pasta digital"):]
    fim = texto.find("Protocolos desta Publicação")
    if fim != -1:
        texto = texto[:fim]
    return "\n".join(l.strip() for l in texto.splitlines() if l.strip())  # tira linhas vazias


def extrair_relacionamentos(soup):
    """Lê a seção oficial 'Relacionamentos desta Matéria' da página da lei.

    No HTML, cada relação é um link assim:
        <a href=".../proposicoes/0/0/1/0/35210" class="menu-opcoes__items">
          <strong>05/01/2012 00:00 - Revoga: </strong>LEI ORDINÁRIA Nº 11471/2012 ...
        </a>
    e vira: {"tipo": "Revoga", "data": "05/01/2012 00:00", "id": "35210", "descricao": "LEI ORDINÁRIA Nº 11471/2012 ..."}

    O soup.select(...) usa seletores CSS: "#id_do_elemento a.classe" = links com essa classe dentro desse elemento.
    Atenção: "Revogada por" inclui revogação PARCIAL (ver calcular_vigencia).
    Obs.: "data" é a data da OUTRA matéria; só existe em coletas feitas depois desta versão do script.
    """
    rels = []
    for a in soup.select("#menu_opcao_proposicao_relacionamentos a.menu-opcoes__items"):
        forte = a.find("strong")
        if not forte:
            continue
        cabecalho = forte.get_text(" ", strip=True)  # "05/01/2012 00:00 - Revoga:"
        tipo = cabecalho.split(" - ", 1)[-1].rstrip(":").strip()
        rels.append({
            "tipo": tipo,
            "data": cabecalho.split(" - ", 1)[0].strip(),
            "id": a.get("href", "").rstrip("/").split("/")[-1],  # o id fica no fim do link
            "descricao": limpar(a.get_text(" ", strip=True)[len(cabecalho):]).strip(),
        })
    return rels


def extrair_anexos(soup):
    """Links dos PDFs anexados à lei (seção "Anexos"). Importante para as leis que só têm PDF.
    Ex.: ["https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1994/236_lei_ordinaria_n_5933_1994.pdf"]"""
    return [a["href"] for a in soup.find_all("a", href=True)
            if a["href"].lower().endswith(".pdf") and "(.pdf)" in a.get_text()]


def baixar_pagina(id_, link):
    """Baixa texto, relacionamentos e anexos da lei, com CACHE em disco.

    Cada lei vira um arquivo cache_textos/<id>.json. Se o arquivo já existe (e é da versão VERSAO_CACHE),
    usa ele e não baixa de novo. Isso permite: (1) retomar a coleta se ela cair; (2) mudar o tratamento
    do texto (ETAPAS 4 e 5) e gerar o leis.json de novo em ~5 min, sem baixar as 14 mil páginas outra vez.
    """
    arq = CACHE / f"{id_}.json"
    if arq.exists():
        dados = json.loads(arq.read_text(encoding="utf-8"))
        if dados.get("versao") == VERSAO_CACHE:
            return dados
    r = baixar(link)
    soup = BeautifulSoup(r.text, "html.parser")
    dados = {
        "versao": VERSAO_CACHE,
        "relacionamentos": extrair_relacionamentos(soup),
        "anexos": extrair_anexos(soup),
        "texto": extrair_texto(soup),  # por último: marcar_riscado altera o soup
    }
    CACHE.mkdir(exist_ok=True)
    arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    time.sleep(PAUSA)
    return dados


# =============================================================================
# ETAPA 4 — TRATAR O TEXTO
# =============================================================================

def processar_texto(texto):
    """Separa o corpo da lei do rodapé do site e procura a data da lei no texto.
    Devolve (corpo, data_assinatura, data_anexo).

    - data_anexo: leis que só têm PDF mostram "Anexos (1)" + "18/10/1994 00:00 -" -> "1994-10-18".
    - corpo: o texto até onde começa o rodapé do site (RE_RODAPE).
    - data_assinatura: a assinatura no fim da lei, ex. "Londrina, 5 de janeiro de 2012." -> "2012-01-05".
      Validada em 425 leis que têm a data no título: acertou 418 (~98%).
    """
    anexo = RE_ANEXO.search(texto)
    # groups() = (dia, mês, ano); o format reordena para ano-mês-dia
    data_anexo = "{2}-{1}-{0}".format(*anexo.groups()) if anexo else None
    m = RE_RODAPE.search(texto)
    corpo = texto[:m.start()] if m else texto  # corta tudo a partir do rodapé
    data_assinatura = None
    a = RE_ASSINATURA.search(sem_riscado(corpo))  # ignora datas em trechos riscados
    if a:
        dia, mes, ano = a.groups()
        mes_n = MESES.get(mes.upper())
        if mes_n:
            data_assinatura = f"{ano.replace('.', '')}-{mes_n:02d}-{int(dia):02d}"  # "1.991" -> "1991"
    return corpo.strip(), data_assinatura, data_anexo


def separar_artigos(texto):
    """Divide o texto da lei em artigos:
        [{"ordem": 1, "artigo": "Art. 1º", "texto": "Art. 1º ...", "texto_riscado": None, "revogado": False}, ...]

    - "ordem" é a posição do artigo e é ÚNICA dentro da lei (use-a como chave no banco).
    - "texto" é só a redação VIGENTE (sem o riscado). Fica "" se o artigo inteiro está riscado.
    - "texto_riscado" é a redação antiga, que não vale mais (None se não houver).
    - "revogado" é True quando o artigo inteiro está riscado.
    - "artigo" (o rótulo) pode se repetir. O caso mais comum é o texto compilado: o "Art. 3º" antigo
      (riscado, revogado=True) seguido do "Art. 3º" com a redação nova.
    """
    # Algumas leis vieram com o texto todo numa linha só. Quebra a linha antes de "Art. N" quando
    # ele vem depois de ".", ":" ou ";" (início de frase). (?<=...) e (?=...) olham antes/depois sem consumir.
    texto = re.sub(r"(?<=[\.:;])\s+(?=Art\.\s*\d)", "\n", texto)
    # split com grupo de captura devolve: [antes, "Art. 1º", corpo1, "Art. 2º", corpo2, ...]
    # Por isso o laço anda de 2 em 2: i = rótulo, i + 1 = corpo do artigo.
    partes = RE_ARTIGO.split(texto)
    artigos = []
    for i in range(1, len(partes), 2):
        rotulo = re.sub(r"\s+", " ", partes[i].replace("⟦", "")).strip().rstrip(".")
        corpo = partes[i + 1] if i + 1 < len(partes) else ""
        completo = (partes[i] + corpo).strip()
        riscado = [t[1:-1].strip() for t in RE_RISCADO.findall(completo)]  # tira o ⟦ e o ⟧
        vigente = sem_riscado(completo).strip()
        artigos.append({
            "ordem": len(artigos) + 1,
            "artigo": rotulo,
            "texto": vigente,
            "texto_riscado": "\n".join(riscado) or None,
            "revogado": not vigente,
        })
    return artigos


# =============================================================================
# MONTAGEM DO REGISTRO DE CADA LEI (junta as ETAPAS 2, 3 e 4)
# =============================================================================

def montar_registro(item):
    """Transforma um item da API no registro padronizado do leis.json (ainda sem texto).

    "id" vem do fim do link ("296902") e é o identificador ÚNICO — use como chave primária.
    "chave"/"numero" NÃO são únicos: existem leis diferentes com o mesmo número (ex.: duas Leis nº 48 de 1949).
    "altera" e "revogada_por" aqui são provisórios: calcular_vigencia (ETAPA 5) monta a versão final.

    Campos de rastreabilidade (não inventam dados; dizem de onde cada informação veio):
      data_lei_fonte    -> "titulo", "assinatura", "anexo" ou None
      data_lei_original -> data encontrada mas impossível (ex.: "2010-02-29"), guardada para revisão
      ementa_fonte      -> "api", "texto" (súmula tirada do texto) ou None (ementa = None)
      revogacao_nota    -> anotação original "(REVOGADA pelo ...)", inclusive quando o revogador
                           não é identificável (decreto, erro de digitação na fonte)
    """
    numero, data_lei, ano, complementar = parse_titulo(item["titulo"])
    ementa = limpar_ementa(item["ementa"])
    link = item["link"].split("#")[0]  # tira o "#pesquisa" do fim
    minha_chave = chave(numero, complementar) if numero else None
    revogada = revogacao_na_ementa(ementa)
    nota = RE_ANOTACAO_REVOGADA.search(ementa)
    data_ok = data_valida(data_lei)
    return {
        "id": link.rstrip("/").split("/")[-1],
        "chave": minha_chave,
        "tipo": "Lei Complementar" if complementar else "Lei",
        "numero": numero,
        "data_lei": data_lei if data_ok else None,
        "data_lei_fonte": "titulo" if data_ok else None,
        "data_lei_original": data_lei if data_lei and not data_ok else None,
        "ano": ano,
        "titulo": limpar(item["titulo"]).strip(),
        "ementa": ementa or None,
        "ementa_fonte": "api" if ementa else None,
        "publicado_site": item["data"],
        "link": link,
        "situacao": "revogada" if revogada is not None else "vigente",
        "revogacao_nota": nota.group(0) if nota else None,
        "complementa_id": None,  # preenchido em calcular_vigencia para "Promulgação de partes vetadas"
        "altera": [c for c in altera_pela_ementa(ementa) if c != minha_chave],  # ignora citar a si mesma
        "alterada_por": [],
        "revoga": [],
        "revogada_por": revogada or [],
        "fonte_relacoes": "ementa",  # vira "cml" quando lermos as relações oficiais (adicionar_texto)
        "relacionamentos": [],
        "anexos": [],
        "artigos": [],
    }


def adicionar_texto(registro):
    """Completa o registro com o que vem da página da lei (ETAPAS 3 e 4).
    Roda em paralelo (3 ao mesmo tempo, ver main). Se o download falhar, marca "erro_texto" e segue."""
    try:
        dados = baixar_pagina(registro["id"], registro["link"])
    except requests.RequestException as e:
        registro["erro_texto"] = str(e)
        return registro
    corpo, data_assinatura, data_anexo = processar_texto(dados["texto"])
    registro["artigos"] = separar_artigos(corpo)
    registro["texto_disponivel"] = bool(registro["artigos"])  # False = só tem PDF ou é inexistente
    registro["relacionamentos"] = dados["relacionamentos"]
    registro["anexos"] = dados.get("anexos", [])
    registro["fonte_relacoes"] = "cml"
    # Impressão digital do texto baixado: numa coleta futura, hash diferente = a página da lei mudou
    registro["hash_texto"] = hashlib.sha256(dados["texto"].encode("utf-8")).hexdigest()
    if "LEI INEXISTENTE" in corpo.upper():
        registro["situacao"] = "inexistente"  # número que ficou vago
    if RE_PROMULGACAO_VETO.search(corpo[:800]):  # só no começo: leis podem citar promulgações no fim
        registro["tipo"] = "Promulgação de partes vetadas"
    if not registro["ementa"]:
        # A API devolveu a ementa vazia: tenta a "SÚMULA:" do próprio texto
        s = RE_SUMULA.search(sem_riscado(corpo)[:3000])
        if s:
            registro["ementa"] = re.sub(r"\s+", " ", s.group(1)).strip()
            registro["ementa_fonte"] = "texto"
    if not registro["data_lei"]:
        # Só aceita a data se o ano bater com o do título. Evita pegar a data errada,
        # como a de uma anotação "(REVOGADA pela Lei ..., de 29 de outubro de 2026)".
        # Data impossível (ex.: 29/02/2010) não entra: fica em data_lei_original para revisão.
        for fonte, data in (("assinatura", data_assinatura), ("anexo", data_anexo)):
            if data and (not registro["ano"] or data[:4] == registro["ano"]):
                if data_valida(data):
                    registro["data_lei"], registro["data_lei_fonte"] = data, fonte
                    break
                registro["data_lei_original"] = registro["data_lei_original"] or data
    return registro


# =============================================================================
# ETAPA 5 — LIGAR AS LEIS E CALCULAR A VIGÊNCIA (a parte central do projeto)
#
# Regras da "situacao":
#   revogada               -> a ementa tem a anotação oficial "(REVOGADA pelo ...)"
#                             (ou é promulgação de partes vetadas de uma lei revogada)
#   inexistente            -> o texto diz "LEI INEXISTENTE" (definido em adicionar_texto)
#   vigente_com_alteracoes -> não revogada, mas foi alterada ou teve PARTE revogada
#   vigente                -> nenhum dos casos acima
#
# Por que "Revogada por" (dos Relacionamentos) não basta para marcar como revogada?
# Porque a Câmara usa esse rótulo também para revogação PARCIAL. Ex.: a Lei 11.471 aparece
# "Revogada por" a 13.529/2022, que só revogou os §§ 1º e 2º do art. 23. A revogação TOTAL
# (pela 14.294/2026) é a que aparece anotada na ementa.
# =============================================================================

CAMPOS_RELACAO = ("altera", "alterada_por", "revoga", "revogada_por")


def resolver_id(c, lei, por_chave, alvo_mais_novo):
    """Acha o id da lei citada pelo número. Quando o número se repete (ex.: duas Leis nº 48 de 1949),
    escolhe pela data: quem altera ou revoga é mais nova do que a lei alterada ou revogada.

    alvo_mais_novo=True  -> a lei citada é a que REVOGOU esta (procura ano >= o desta, a mais antiga delas)
    alvo_mais_novo=False -> a lei citada é a ALTERADA por esta (procura ano <= o desta, a mais recente delas)
    """
    candidatas = por_chave.get(c, [])
    if len(candidatas) > 1 and lei["ano"]:
        if alvo_mais_novo:
            filtradas = sorted((x for x in candidatas if (x["ano"] or "") >= lei["ano"]), key=lambda x: x["ano"])
        else:
            filtradas = sorted((x for x in candidatas if (x["ano"] or "9999") <= lei["ano"]), key=lambda x: x["ano"])[::-1]
        candidatas = filtradas or candidatas
    return candidatas[0]["id"] if candidatas else None


def adicionar_relacao(lei, tipo, id_, c):
    """Acrescenta {"tipo", "id", "chave"} em lei["relacoes"], sem deixar entrar repetida.

    Descarta relação da lei com ELA MESMA: em ~27 páginas a própria Câmara lista a lei como
    "Revoga: ela mesma" (ex.: Lei 9.282), e a anotação da Lei 9.265 diz que ela foi revogada
    "pela Lei nº 9.265" (número errado na fonte). A lista crua "relacionamentos" continua como veio.
    """
    if (id_ and id_ == lei["id"]) or (not id_ and c == lei["chave"]):
        return
    for r in lei["relacoes"]:
        if r["tipo"] == tipo and ((id_ and r["id"] == id_) or (not id_ and r["chave"] == c)):
            return
    lei["relacoes"].append({"tipo": tipo, "id": id_, "chave": c})


def calcular_vigencia(leis):
    """Monta lei["relacoes"] (lista de {tipo, id, chave}; id é None se a lei citada não está no arquivo),
    preenche as listas de chaves altera/alterada_por/revoga/revogada_por e define a situação.

    Exemplo completo (Lei 11.471, id 35210):
        ementa: "(REVOGADA pelo Art. 225. da Lei nº 14.294 ...)"  -> revogada_por 14294 (revogação total)
        Relacionamentos: Revogada por 14.294, Revogada por 13.529, Revoga 10.283
        resultado: situacao "revogada", revogada_por ["14294", "13529"], revoga ["10283"]
    """
    # Índices para achar uma lei rápido: pelo id (único) e pela chave (pode ter mais de uma lei)
    por_id = {l["id"]: l for l in leis}
    por_chave = {}
    for l in leis:
        if l["chave"]:
            por_chave.setdefault(l["chave"], []).append(l)

    # Guarda o que foi deduzido em montar_registro antes de reconstruir as relações do zero
    deduzidas = {l["id"]: {"altera": l["altera"], "revogada_por": l["revogada_por"]} for l in leis}
    for l in leis:
        l["relacoes"] = []

    for lei in leis:
        # 1) Revogação total anotada na ementa (vale para qualquer fonte)
        for c in deduzidas[lei["id"]]["revogada_por"]:
            adicionar_relacao(lei, "revogada_por", resolver_id(c, lei, por_chave, True), c)

        if lei["fonte_relacoes"] == "cml":
            # 2a) Relações oficiais da seção "Relacionamentos desta Matéria"
            for rel in lei["relacionamentos"]:
                tipo = RELACOES.get(rel["tipo"])  # "Revogada por" -> "revogada_por"
                if tipo not in CAMPOS_RELACAO:   # ignora Cita, Sanção, Vínculo...
                    continue
                alvo = por_id.get(rel["id"])
                if alvo:
                    adicionar_relacao(lei, tipo, alvo["id"], alvo["chave"])
                elif rel["descricao"].upper().startswith("LEI"):  # lei fora do arquivo: tira o número da descrição
                    numero, _, _, complementar = parse_titulo(rel["descricao"][:80])
                    if numero:
                        adicionar_relacao(lei, tipo, None, chave(numero, complementar))
        else:
            # 2b) Sem texto (plano B): alterações deduzidas da ementa
            for c in deduzidas[lei["id"]]["altera"]:
                adicionar_relacao(lei, "altera", resolver_id(c, lei, por_chave, False), c)

    # 3) Completa o lado inverso nas leis que NÃO têm as relações oficiais
    #    (as que têm já trazem os dois lados: "Altera" numa página, "Alterada por" na outra)
    inverso = {"altera": "alterada_por", "revogada_por": "revoga"}
    for lei in leis:
        for r in list(lei["relacoes"]):
            alvo = por_id.get(r["id"]) if r["id"] else None
            if r["tipo"] in inverso and alvo and alvo["fonte_relacoes"] != "cml":
                adicionar_relacao(alvo, inverso[r["tipo"]], lei["id"], lei["chave"])

    # 4) Listas de chaves (para leitura humana) e situação final
    for lei in leis:
        for campo in CAMPOS_RELACAO:
            # dict.fromkeys remove repetidos mantendo a ordem
            lei[campo] = list(dict.fromkeys(r["chave"] for r in lei["relacoes"] if r["tipo"] == campo and r["chave"]))
        # "Revogada por" sem a anotação de REVOGADA na ementa = revogação parcial (só alguns dispositivos)
        if lei["situacao"] == "vigente" and (lei["alterada_por"] or lei["revogada_por"]):
            lei["situacao"] = "vigente_com_alteracoes"

    # 5) Promulgação de partes vetadas: liga à lei principal (mesmo número, outro id).
    #    Ex.: id 249902 complementa a Lei 13.960 (id 242406). Os artigos dela FAZEM PARTE da lei principal,
    #    e ela segue a situação da principal se esta tiver sido revogada.
    for lei in leis:
        if lei["tipo"] != "Promulgação de partes vetadas":
            continue
        principais = [x for x in por_chave.get(lei["chave"], []) if x["id"] != lei["id"] and x["tipo"] != lei["tipo"]]
        principais.sort(key=lambda x: x["ano"] != lei["ano"])  # prefere a do mesmo ano
        if principais:
            lei["complementa_id"] = principais[0]["id"]
            if principais[0]["situacao"] == "revogada":
                lei["situacao"] = "revogada"
    return leis


# =============================================================================
# ETAPA 6 — JUNTAR TUDO E SALVAR (main)
# =============================================================================

def commit_do_script():
    """Commit do git em que o script estava ao gerar o arquivo (+ aviso se tinha alterações não commitadas)."""
    try:
        pasta = Path(__file__).parent
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=pasta,
                                capture_output=True, text=True, check=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain", "--", Path(__file__).name], cwd=pasta,
                              capture_output=True, text=True).stdout.strip()
        return commit + ("+alteracoes_locais" if sujo else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def reaplicar_anotacao_revogada(leis):
    """Relê a anotação "(REVOGADA ...)" das ementas com a regra atual, sem baixar nada.

    Serve para corrigir um leis.json já coletado quando a regra de leitura muda.
    Ex.: a Lei 13.905/2024 estava "revogada" porque a anotação "(Revogado pelo Decreto 1.341...)"
    falava do Decreto 413, citado logo antes na ementa. Devolve a lista de leis corrigidas.
    """
    corrigidas = []
    por_id = {l["id"]: l for l in leis}
    for lei in leis:
        nota = RE_ANOTACAO_REVOGADA.search(lei["ementa"] or "")
        nova = nota.group(0) if nota else None
        if nova == lei["revogacao_nota"]:
            continue
        if nova is not None or lei["situacao"] != "revogada":
            raise ValueError(f"Lei {lei['id']}: anotação de revogação mudou de forma inesperada.")
        if refs_leis(lei["revogacao_nota"] or ""):
            raise ValueError(f"Lei {lei['id']}: a anotação descartada citava uma lei.")
        principal = por_id.get(lei.get("complementa_id"))
        if principal and principal["situacao"] == "revogada":
            continue  # segue a lei principal (Promulgação de partes vetadas)
        antes = lei["situacao"]
        lei["revogacao_nota"] = None
        # Mesma regra de calcular_vigencia: sem revogação total, alterações = "vigente_com_alteracoes"
        lei["situacao"] = "vigente_com_alteracoes" if (lei["alterada_por"] or lei["revogada_por"]) else "vigente"
        corrigidas.append((lei, antes))
    return corrigidas


def gerar_meta(leis, saida, args, reprocessamento=None):
    """Gera <saida>.meta.json (ex.: leis.meta.json) descrevendo como o leis.json foi produzido:
    versão do formato, quando foi gerado, quando os textos foram baixados, commit do script, totais
    e o hash SHA-256 do arquivo (para conferir se o leis.json é exatamente o que foi gerado)."""
    caminho = Path(saida)
    datas_cache = [(CACHE / f"{l['id']}.json").stat().st_mtime for l in leis
                   if "hash_texto" in l and (CACHE / f"{l['id']}.json").exists()]

    def iso(ts):
        return datetime.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")

    artigos = [a for l in leis for a in l["artigos"]]
    meta = {
        "versao_formato": VERSAO_FORMATO,
        "gerado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "textos_baixados_entre": [iso(min(datas_cache)), iso(max(datas_cache))] if datas_cache else None,
        "fonte": {"api": API, "call": "legislacoes", "tipo": "Leis"},
        "script": {"arquivo": "coleta_leis.py", "commit": commit_do_script(),
                   "opcoes": {"texto": args.texto, "paginas": args.paginas}},
        "totais": {
            "leis": len(leis),
            "por_situacao": dict(Counter(l["situacao"] for l in leis)),
            "por_tipo": dict(Counter(l["tipo"] for l in leis)),
            "artigos": len(artigos),
            "artigos_revogados": sum(a["revogado"] for a in artigos),
            "artigos_com_texto_riscado": sum(bool(a["texto_riscado"]) for a in artigos),
            "relacoes": sum(len(l["relacoes"]) for l in leis),
            "relacionamentos_cml": sum(len(l["relacionamentos"]) for l in leis),
            "sem_data_lei": sum(not l["data_lei"] for l in leis),
            "sem_texto": sum(not l.get("texto_disponivel") for l in leis),
            "sem_ementa": sum(not l["ementa"] for l in leis),
        },
        "arquivo": {"nome": caminho.name, "bytes": caminho.stat().st_size,
                    "sha256": hashlib.sha256(caminho.read_bytes()).hexdigest()},
    }
    # Mesmo hash no nível de cima: é a chave que o carregar_leis.py (carga no Postgres) confere
    meta["sha256_leis_json"] = meta["arquivo"]["sha256"]
    if reprocessamento:
        meta["reprocessamento"] = reprocessamento
    arq_meta = caminho.with_suffix(".meta.json")
    arq_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return arq_meta


def main():
    # Opções de linha de comando (python coleta_leis.py --help mostra todas)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paginas", type=int, help="máximo de páginas da API (50 leis cada)")
    ap.add_argument("--texto", action="store_true", help="baixa texto e relacionamentos de cada lei")
    ap.add_argument("--paralelo", type=int, default=3, help="downloads simultâneos de texto (padrão 3)")
    ap.add_argument("--saida", default="leis.json")
    ap.add_argument("--reprocessar", metavar="ARQUIVO",
                    help="relê as anotações de um leis.json já coletado com as regras atuais (sem baixar nada)")
    args = ap.parse_args()
    if args.reprocessar:
        return reprocessar(args)
    if not TOKEN:
        raise SystemExit("Defina CML_TOKEN no arquivo .env")

    # ETAPAS 1 e 2: lista as leis e lê título/ementa
    leis = [montar_registro(item) for item in listar_leis(max_paginas=args.paginas)]

    # ETAPAS 3 e 4: baixa e trata o texto de cada lei, 3 ao mesmo tempo (ThreadPoolExecutor).
    # Com 3 downloads simultâneos a coleta completa cai de ~6 h para ~1h10. Não usamos mais
    # para não sobrecarregar o site da Câmara. pool.map mantém a ordem original das leis.
    if args.texto:
        with ThreadPoolExecutor(max_workers=args.paralelo) as pool:
            for i, _ in enumerate(pool.map(adicionar_texto, leis), 1):
                if i % 100 == 0:
                    print(f"textos: {i}/{len(leis)}", flush=True)

    # ETAPA 5: liga as leis e define a situação de cada uma
    leis = calcular_vigencia(leis)

    # Salva. ensure_ascii=False mantém os acentos legíveis; indent=2 deixa o arquivo formatado.
    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)
    resumo = dict(Counter(l["situacao"] for l in leis))
    erros = sum("erro_texto" in l for l in leis)
    print(f"{len(leis)} leis salvas em {args.saida} -> {resumo}" + (f" ({erros} sem texto)" if erros else ""))

    # Arquivo de metadados ao lado do leis.json (não muda a estrutura do leis.json, que continua uma lista)
    print(f"metadados em {gerar_meta(leis, args.saida, args)}")


def reprocessar(args):
    """python coleta_leis.py --reprocessar leis.json: corrige o arquivo sem nova coleta.
    As opções da coleta original (texto, páginas) são preservadas nos metadados."""
    entrada = Path(args.reprocessar)
    leis = json.loads(entrada.read_text(encoding="utf-8"))
    anterior = entrada.with_suffix(".meta.json")
    meta_antiga = json.loads(anterior.read_text(encoding="utf-8")) if anterior.exists() else {}
    corrigidas = reaplicar_anotacao_revogada(leis)
    for lei, antes in corrigidas:
        print(f"Lei {lei['chave']}/{lei['ano']} (id {lei['id']}): {antes} -> {lei['situacao']}")
    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(leis, f, ensure_ascii=False, indent=2)
    opcoes = (meta_antiga.get("script") or {}).get("opcoes") or {"texto": True, "paginas": None}
    origem = argparse.Namespace(texto=opcoes.get("texto"), paginas=opcoes.get("paginas"))
    info = {"em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "motivo": "anotação de revogação que cita só decreto não revoga a lei",
            "sha256_anterior": (meta_antiga.get("arquivo") or {}).get("sha256"),
            "leis_corrigidas": [l["id"] for l, _ in corrigidas]}
    print(f"{len(corrigidas)} lei(s) corrigida(s); metadados em {gerar_meta(leis, args.saida, origem, info)}")


# Só roda main() quando o arquivo é executado direto (python coleta_leis.py),
# não quando é importado por outro script (import coleta_leis).
if __name__ == "__main__":
    main()
