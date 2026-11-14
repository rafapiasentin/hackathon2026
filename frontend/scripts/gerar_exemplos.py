"""
Gera os arquivos de exemplo do validador de leis (frontend/public/exemplos/).

São textos de EXEMPLO para testar o validador, adaptados de leis de Londrina.
Não são o texto oficial das leis.

Requisitos: pip install pillow fpdf2
Uso:        python scripts/gerar_exemplos.py
"""
import os
import random
from pathlib import Path

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SAIDA = Path(__file__).resolve().parent.parent / "public" / "exemplos"
FONTES = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
AVISO = "Documento de exemplo para teste do validador. Não é o texto oficial da lei."

PREAMBULO = (
    "A CÂMARA MUNICIPAL DE LONDRINA, ESTADO DO PARANÁ, APROVOU E EU, "
    "PREFEITO DO MUNICÍPIO, SANCIONO A SEGUINTE LEI:"
)

# ------------------------------------------------------------------ textos

CONFORME = [
    ("titulo", "LEI Nº 14.300, DE 11 DE NOVEMBRO DE 2026"),
    ("ementa", "SÚMULA: Institui o Dia Municipal do Enfermeiro no Calendário de Comemorações Oficiais do Município de Londrina."),
    ("preambulo", PREAMBULO),
    ("texto", "Art. 1º Fica incluído, no Calendário de Comemorações Oficiais do Município de Londrina, o Dia Municipal do Enfermeiro, a ser celebrado anualmente no dia 12 de maio."),
    ("texto", "Parágrafo único. As atividades alusivas à data poderão incluir:"),
    ("inciso", "I - palestras sobre a profissão;"),
    ("inciso", "II - campanhas de saúde;"),
    ("inciso", "III - homenagens a profissionais da rede municipal."),
    ("texto", "Art. 2º Esta Lei entra em vigor na data de sua publicação."),
    ("fecho", "Londrina, 11 de novembro de 2026."),
    ("assinatura", "PREFEITO DO MUNICÍPIO"),
]

FORA_DO_PADRAO = [
    ("titulo", "Lei nº 14310, de 25/11/2026"),
    ("preambulo", PREAMBULO),
    ("texto", "Art. 1º Fica instituído o Programa Municipal de Hortas Comunitárias."),
    ("texto", "§ único. O Programa será coordenado pela Secretaria Municipal de Agricultura e Abastecimento."),
    ("texto", "Art. 2 São objetivos do Programa:"),
    ("inciso", "1 - incentivar a alimentação saudável;"),
    ("inciso", "2 - ocupar com hortas as áreas públicas sem uso."),
    ("texto", "Art. 4º O Poder Executivo regulamentará esta Lei no prazo de noventa dias."),
    ("texto", "Art. 5º Esta Lei entra em vigor na data de sua publicação."),
    ("texto", "Art. 6º Revogam-se as disposições em contrário."),
    ("fecho", "Londrina, 25/11/2026."),
    ("assinatura", "PREFEITO DO MUNICÍPIO"),
]

ESCANEADA = [
    ("titulo", "LEI Nº 14.296, DE 4 DE NOVEMBRO DE 2026"),
    ("ementa", "SÚMULA: Garante recesso escolar aos professores e profissionais do magistério da Rede Municipal de Ensino de Londrina."),
    ("preambulo", PREAMBULO),
    ("texto", "Art. 1º Fica garantido recesso escolar aos professores e aos profissionais do magistério da Rede Municipal de Ensino."),
    ("texto", "Art. 2º O período de recesso será definido no calendário escolar anual."),
    ("texto", "Art. 3º Esta Lei entra em vigor na data de sua publicação."),
    ("texto", "Art. 4º Revogam-se as disposições em contrário."),
    ("fecho", "Londrina, 4 de novembro de 2026."),
    ("assinatura", "PREFEITO DO MUNICÍPIO"),
]

XML = """<?xml version="1.0" encoding="UTF-8"?>
<!-- {aviso} -->
<LexML xmlns="http://www.lexml.gov.br/1.0">
  <Metadado>
    <Identificacao URN="urn:lex:br;parana;londrina:municipal:lei:2026-10-29;14294"/>
  </Metadado>
  <Norma>
    <ParteInicial>
      <Epigrafe id="epigrafe">LEI Nº 14.294, DE 29 DE OUTUBRO DE 2026</Epigrafe>
      <Ementa id="ementa">Institui o Código Ambiental do Município de Londrina.</Ementa>
      <Preambulo id="preambulo"><p>{preambulo}</p></Preambulo>
    </ParteInicial>
    <Articulacao>
      <Artigo id="art1">
        <Rotulo>Art. 1º</Rotulo>
        <Caput id="art1_cpt"><p>Esta Lei institui o Código Ambiental do Município de Londrina, com normas de proteção, conservação e recuperação do meio ambiente.</p></Caput>
      </Artigo>
      <Artigo id="art2">
        <Rotulo>Art. 2º</Rotulo>
        <Caput id="art2_cpt">
          <p>São objetivos do Código Ambiental:</p>
          <Inciso id="art2_cpt_inc1"><Rotulo>I -</Rotulo><p>proteger os fundos de vale e as nascentes;</p></Inciso>
          <Inciso id="art2_cpt_inc2"><Rotulo>II -</Rotulo><p>incentivar a arborização urbana;</p></Inciso>
          <Inciso id="art2_cpt_inc3"><Rotulo>III -</Rotulo><p>promover a educação ambiental.</p></Inciso>
        </Caput>
        <Paragrafo id="art2_par1"><Rotulo>§ 1º</Rotulo><p>Os objetivos serão detalhados em regulamento.</p></Paragrafo>
      </Artigo>
      <Artigo id="art3">
        <Rotulo>Art. 3º</Rotulo>
        <Caput id="art3_cpt"><p>Fica revogada a Lei nº 11.471, de 2012.</p></Caput>
      </Artigo>
      <Artigo id="art4">
        <Rotulo>Art. 4º</Rotulo>
        <Caput id="art4_cpt"><p>Esta Lei entra em vigor na data de sua publicação.</p></Caput>
      </Artigo>
    </Articulacao>
    <ParteFinal>
      <LocalDataFecho>Londrina, 29 de outubro de 2026.</LocalDataFecho>
    </ParteFinal>
  </Norma>
</LexML>
"""

# ------------------------------------------------------------------ PDF com texto

ESTILO = {
    "titulo": dict(estilo="B", tam=12, alinhar="C", antes=0, recuo=0),
    "ementa": dict(estilo="", tam=11, alinhar="J", antes=8, recuo=70),
    "preambulo": dict(estilo="", tam=11, alinhar="J", antes=8, recuo=0),
    "texto": dict(estilo="", tam=11, alinhar="J", antes=6, recuo=0),
    "inciso": dict(estilo="", tam=11, alinhar="J", antes=2, recuo=10),
    "fecho": dict(estilo="", tam=11, alinhar="C", antes=12, recuo=0),
    "assinatura": dict(estilo="B", tam=11, alinhar="C", antes=14, recuo=0),
}


def pdf_texto(blocos, arquivo):
    pdf = FPDF(format="A4")
    pdf.set_margins(25, 25, 25)
    pdf.add_page()
    pdf.add_font("Serifa", "", str(FONTES / "times.ttf"))
    pdf.add_font("Serifa", "B", str(FONTES / "timesbd.ttf"))
    pdf.add_font("Serifa", "I", str(FONTES / "timesi.ttf"))
    for tipo, texto in blocos:
        e = ESTILO[tipo]
        pdf.ln(e["antes"])
        pdf.set_font("Serifa", e["estilo"], e["tam"])
        pdf.set_x(25 + e["recuo"])
        pdf.multi_cell(0, 6, texto, align=e["alinhar"])
    pdf.set_auto_page_break(False)
    pdf.set_y(-20)
    pdf.set_font("Serifa", "I", 8)
    pdf.cell(0, 5, AVISO, align="C")
    pdf.output(str(arquivo))


# ------------------------------------------------------------------ PDF escaneado (só imagem)


def quebrar(texto, fonte, largura, desenho):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if desenho.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def pdf_escaneado(blocos, arquivo):
    random.seed(7)
    dpi = 150
    larg, alt = int(8.27 * dpi), int(11.69 * dpi)
    img = Image.new("L", (larg, alt), 246)
    d = ImageDraw.Draw(img)
    normal = ImageFont.truetype(str(FONTES / "times.ttf"), 27)
    negrito = ImageFont.truetype(str(FONTES / "timesbd.ttf"), 27)
    margem, y = 150, 170
    util = larg - 2 * margem
    for tipo, texto in blocos:
        e = ESTILO[tipo]
        y += int(e["antes"] * 2.6)
        fonte = negrito if e["estilo"] == "B" else normal
        recuo = int(e["recuo"] * 5.9)
        for linha in quebrar(texto, fonte, util - recuo, d):
            w = d.textlength(linha, font=fonte)
            x = margem + recuo if e["alinhar"] in ("J", "L") else margem + (util - w) / 2
            d.text((x, y), linha, fill=28, font=fonte)
            y += 38
    pequena = ImageFont.truetype(str(FONTES / "timesi.ttf"), 16)
    d.text(((larg - d.textlength(AVISO, font=pequena)) / 2, alt - 110), AVISO, fill=90, font=pequena)
    # aparência de papel escaneado: leve rotação, ruído e borrão
    img = img.rotate(0.5, resample=Image.BICUBIC, fillcolor=238)
    ruido = Image.effect_noise((larg, alt), 10).point(lambda p: 255 if p > 120 else 236)
    img = Image.blend(img, ruido.convert("L"), 0.06).filter(ImageFilter.GaussianBlur(0.5))
    img.convert("RGB").save(arquivo, "PDF", resolution=dpi)


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    pdf_texto(CONFORME, SAIDA / "lei-no-padrao.pdf")
    pdf_texto(FORA_DO_PADRAO, SAIDA / "lei-fora-do-padrao.pdf")
    pdf_escaneado(ESCANEADA, SAIDA / "lei-escaneada.pdf")
    (SAIDA / "lei-codigo-ambiental.xml").write_text(XML.format(aviso=AVISO, preambulo=PREAMBULO), encoding="utf-8")
    for f in sorted(SAIDA.iterdir()):
        print(f"{f.name}: {f.stat().st_size // 1024} KB")
