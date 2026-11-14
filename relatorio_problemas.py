"""Gera o relatório das leis com problemas nos dados de origem (e como cada um foi tratado).

Uso (depois de rodar coleta_leis.py --texto):
    python relatorio_problemas.py

Lê leis.json e gera:
    docs/PROBLEMAS_NOS_DADOS.md   -> explicação de cada problema + lista de todas as leis afetadas
    docs/leis_com_problemas.csv   -> uma linha por (lei, problema), para filtrar ou carregar no banco
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import coleta_leis as c

# Cada problema: código -> (título, o que aconteceu na fonte, como foi resolvido)
PROBLEMAS = {
    "texto_riscado": (
        "Redação antiga riscada no texto compilado",
        "A página da Câmara mostra o texto compilado: quando um artigo muda, a redação antiga continua lá, "
        "riscada, e a nova vem logo depois. O script antigo extraía as duas como se valessem.",
        "Cada trecho riscado é separado: `texto` traz só a redação vigente, `texto_riscado` a antiga, e "
        "`revogado = true` quando o artigo inteiro está riscado. O chatbot usa só `texto` de artigos não revogados.",
    ),
    "sem_data": (
        "Lei sem data",
        "Leis antigas têm título no formato `LEI ORDINÁRIA Nº 1234/1965`, só com o ano, e o texto não traz "
        "assinatura com data nem anexo datado.",
        "`data_lei = null`. Nada é inventado; o `ano` (tirado do título) está sempre preenchido e pode ser usado "
        "para filtrar por período.",
    ),
    "data_impossivel": (
        "Data impossível no texto",
        "O texto traz uma data que não existe no calendário (ex.: \"29 de fevereiro de 2010\").",
        "A data impossível não entra em `data_lei`: fica em `data_lei_original` para revisão. O script tenta a "
        "próxima fonte (anexo); `data_lei_fonte` diz de onde veio a data usada.",
    ),
    "autorrelacao": (
        "Relação da lei com ela mesma",
        "Na seção \"Relacionamentos desta Matéria\", a própria Câmara lista a lei como \"Revoga\", \"Altera\" ou "
        "\"Revogada por\" ela mesma.",
        "A relação é descartada em `relacoes` (usada para a vigência). A lista crua `relacionamentos` continua "
        "como veio da fonte.",
    ),
    "anotacao_numero_errado": (
        "Anotação de revogação cita a própria lei",
        "A anotação \"(REVOGADA pelo ... da Lei nº X ...)\" traz como revogador o número da própria lei "
        "(erro de digitação na fonte).",
        "A lei continua `revogada` (a anotação existe), mas o número errado não vira relação. A anotação original "
        "fica em `revogacao_nota`; o revogador correto, quando a Câmara o lista nos Relacionamentos, entra em "
        "`revogada_por`.",
    ),
    "revogada_sem_revogador": (
        "Revogada sem lei revogadora identificável",
        "A anotação de revogação cita um decreto (não uma lei) ou veio quebrada da fonte "
        "(ex.: \"Lei nº de de de 20\").",
        "`situacao = revogada` e `revogada_por` vazio. A anotação original fica em `revogacao_nota` como evidência.",
    ),
    "ementa_vazia": (
        "Ementa vazia na API",
        "A API devolveu a ementa (súmula) em branco.",
        "Quando o texto traz \"SÚMULA:\", ela é usada (`ementa_fonte = \"texto\"`). Senão, `ementa = null` "
        "(`ementa_fonte = null`).",
    ),
    "promulgacao_veto": (
        "Promulgação de partes vetadas com o mesmo número",
        "Trechos vetados pelo prefeito e promulgados depois pela Câmara aparecem como outra \"lei\" com o mesmo "
        "número, o que parecia duplicata.",
        "`tipo = \"Promulgação de partes vetadas\"` e `complementa_id` apontando para a lei principal. Os artigos "
        "fazem parte da lei principal e seguem a situação dela.",
    ),
    "numero_repetido": (
        "Leis diferentes com o mesmo número",
        "Duas matérias distintas registradas com o mesmo número e ano.",
        "O identificador é o `id` da Câmara (único). `chave`/`numero` não podem ser chave primária nem `UNIQUE`.",
    ),
    "so_pdf": (
        "Lei só com PDF (sem texto em HTML)",
        "A página não tem o texto da lei, só um PDF anexado.",
        "`texto_disponivel = false`, `artigos` vazio e o link do PDF em `anexos`. Não entra na busca por artigo; "
        "a leitura dos PDFs é um próximo passo.",
    ),
    "inexistente": (
        "Número de lei inexistente",
        "A página diz \"LEI INEXISTENTE\": o número ficou vago.",
        "`situacao = \"inexistente\"` e `texto_disponivel = false`. Não entra na busca.",
    ),
}


def detectar(leis):
    """Devolve {codigo_problema: [(lei, detalhe), ...]}."""
    por_chave = defaultdict(list)
    for l in leis:
        por_chave[l["chave"]].append(l)
    achados = defaultdict(list)
    for l in leis:
        rev = [a["artigo"] for a in l["artigos"] if a["revogado"]]
        ris = [a["artigo"] for a in l["artigos"] if a["texto_riscado"] and not a["revogado"]]
        if rev or ris:
            partes = []
            if rev:
                partes.append(f"{len(rev)} artigo(s) revogado(s): {', '.join(rev[:6])}{'…' if len(rev) > 6 else ''}")
            if ris:
                partes.append(f"{len(ris)} com trecho riscado: {', '.join(ris[:6])}{'…' if len(ris) > 6 else ''}")
            achados["texto_riscado"].append((l, "; ".join(partes)))
        if not l["data_lei"] and not l["data_lei_original"]:
            achados["sem_data"].append((l, f"ano {l['ano']}"))
        if l["data_lei_original"]:
            achados["data_impossivel"].append((l, f"texto: {l['data_lei_original']} → usada: {l['data_lei'] or '—'} ({l['data_lei_fonte'] or 'sem fonte'})"))
        # só os rótulos que contam para a vigência (Altera, Alterada por, Revoga, Revogada por)
        auto = [r["tipo"] for r in l["relacionamentos"]
                if r["id"] == l["id"] and c.RELACOES.get(r["tipo"]) in c.CAMPOS_RELACAO]
        if auto:
            achados["autorrelacao"].append((l, "Câmara lista: " + ", ".join(f"{t}: ela mesma" for t in auto)))
        nota = l["revogacao_nota"] or ""
        if nota and l["chave"] in c.refs_leis(nota):
            achados["anotacao_numero_errado"].append((l, f"{nota} → revogada_por: {l['revogada_por'] or '—'}"))
        if l["situacao"] == "revogada" and not l["revogada_por"]:
            achados["revogada_sem_revogador"].append((l, nota))
        if l["ementa_fonte"] != "api":
            achados["ementa_vazia"].append((l, "súmula tirada do texto" if l["ementa_fonte"] == "texto" else "ementa = null"))
        if l["tipo"] == "Promulgação de partes vetadas":
            achados["promulgacao_veto"].append((l, f"complementa_id: {l['complementa_id']}"))
        if len(por_chave[l["chave"]]) > 1 and l["tipo"] != "Promulgação de partes vetadas":
            outras = [x["id"] for x in por_chave[l["chave"]] if x["id"] != l["id"]]
            achados["numero_repetido"].append((l, "mesmo número que id " + ", ".join(outras)))
        if not l.get("texto_disponivel") and l["situacao"] != "inexistente":
            achados["so_pdf"].append((l, l["anexos"][0] if l["anexos"] else "sem link de PDF"))
        if l["situacao"] == "inexistente":
            achados["inexistente"].append((l, "LEI INEXISTENTE"))
    return achados


def fmt(n):
    """1496 -> "1.496" (separador de milhar brasileiro)."""
    return f"{n:,}".replace(",", ".")


def nome_lei(l):
    return f"[{l['titulo']}]({l['link']})"


def main():
    leis = json.load(open("leis.json", encoding="utf-8"))
    meta = json.load(open("leis.meta.json", encoding="utf-8")) if Path("leis.meta.json").exists() else {}
    achados = detectar(leis)
    afetadas = {l["id"] for itens in achados.values() for l, _ in itens}
    artigos = [a for l in leis for a in l["artigos"]]

    md = ["# Problemas encontrados nos dados das leis", "",
          "Relatório gerado por `relatorio_problemas.py` a partir do `leis.json`"
          + (f" de {meta['gerado_em'][:10]} (SHA-256 `{meta['arquivo']['sha256'][:12]}…`)" if meta else "") + ".",
          "Os problemas abaixo estão **na fonte** (site e API da Câmara). O script não corrige a fonte: ele trata cada caso "
          "e deixa registrado de onde veio cada informação.", "",
          f"**{fmt(len(afetadas))} de {fmt(len(leis))} leis** têm pelo menos um problema tratado. Uma lei pode aparecer em mais de uma categoria.", "",
          "## Resumo", "",
          "| Problema | Leis afetadas | Como foi resolvido |", "|---|---|---|"]
    for cod, (titulo, _, solucao) in PROBLEMAS.items():
        n = len(achados.get(cod, []))
        if n:
            md.append(f"| [{titulo}](#{cod.replace('_', '-')}) | {fmt(n)} | {solucao} |")
    md += ["", f"Só no texto riscado: **{fmt(sum(a['revogado'] for a in artigos))} artigos revogados por inteiro** e "
           f"**{fmt(sum(bool(a['texto_riscado']) and not a['revogado'] for a in artigos))} artigos com algum trecho riscado**.", ""]

    for cod, (titulo, causa, solucao) in PROBLEMAS.items():
        itens = achados.get(cod, [])
        if not itens:
            continue
        md += [f'<a id="{cod.replace("_", "-")}"></a>', f"## {titulo} ({fmt(len(itens))} leis)", "",
               f"**O que aconteceu:** {causa}", "", f"**Solução:** {solucao}", "",
               "| Lei | id | Detalhe |", "|---|---|---|"]
        for l, detalhe in sorted(itens, key=lambda x: (x[0]["ano"] or "", x[0]["numero"] or ""), reverse=True):
            md.append(f"| {nome_lei(l)} | {l['id']} | {detalhe.replace('|', '/')} |")
        md.append("")

    Path("docs").mkdir(exist_ok=True)
    Path("docs/PROBLEMAS_NOS_DADOS.md").write_text("\n".join(md), encoding="utf-8")
    with open("docs/leis_com_problemas.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "chave", "ano", "titulo", "problema", "detalhe", "solucao", "link"])
        for cod, itens in achados.items():
            for l, detalhe in itens:
                w.writerow([l["id"], l["chave"], l["ano"], l["titulo"], PROBLEMAS[cod][0], detalhe, PROBLEMAS[cod][2], l["link"]])

    print(f"{len(afetadas)} leis afetadas de {len(leis)}")
    for cod in PROBLEMAS:
        print(f"  {cod}: {len(achados.get(cod, []))}")


if __name__ == "__main__":
    main()
