// Dados de exemplo para o front funcionar antes do backend existir.
// Os números, ementas e relações vêm do site da Câmara (CML); onde não temos
// o texto real do artigo, o texto diz isso. A situação das leis antigas é ilustrativa
// até o leis.json real ser carregado. Não use estas respostas como orientação real.
import type { Lei, Resposta } from "./types";

export const PENDENTE = "Texto completo disponível quando o front estiver ligado ao banco de leis.";

const DECRETO_466 =
  "Regulamenta procedimentos para emissão de Consulta Prévia e Diretrizes Urbanísticas de Parcelamento do Solo, nos termos da Lei Municipal nº 13.898 de 20 de dezembro de 2024, em especial, artigos 22, 50 e 56 e parágrafo único do artigo 111 da Lei Municipal nº 13.905 de 20 de dezembro de 2024 e dá outras providências.";

// Par de EXEMPLO (inventado) para a tela "O que mudou": uma lei de 1980, escrita no padrão antigo,
// substituída por uma lei de 2026 no padrão da LC 95/1998.
const EXEMPLO_1980: Lei = {
  id: "exemplo-1980",
  chave: "3105",
  ano: "1980",
  data_lei: "1980-05-12",
  titulo: "Lei nº 3105 de 12/05/1980",
  ementa: "Dispõe sobre a poda, o corte e o plantio de árvores no Município de Londrina.",
  situacao: "revogada",
  link: "",
  exemplo: true,
  relacoes: [
    { tipo: "alterada_por", id: null, chave: "4512" },
    { tipo: "revogada_por", id: "exemplo-2026", chave: "14320" },
  ],
  artigos: [
    { ordem: 1, artigo: "Art. 1º", texto: "Art. 1º - A poda e o corte de árvores em vias públicas dependem de autorização da Prefeitura Municipal." },
    { ordem: 2, artigo: "Art. 2º", texto: "Art. 2º - O pedido de autorização deverá ser feito por escrito, no protocolo da Prefeitura, com prazo de resposta de 30 (trinta) dias." },
    { ordem: 3, artigo: "Art. 3º", texto: "Art. 3º - Fica proibido o corte de árvores nativas em terrenos particulares sem licença." },
    { ordem: 4, artigo: "Art. 4º", texto: "Art. 4º - O infrator pagará multa de 5 (cinco) salários mínimos por árvore cortada." },
    { ordem: 5, artigo: "Art. 5º", texto: "Art. 5º - As árvores plantadas em calçadas deverão ser de espécies ornamentais." },
    { ordem: 6, artigo: "Art. 6º", texto: "Art. 6º - A Prefeitura manterá viveiro municipal para o fornecimento gratuito de mudas." },
    { ordem: 7, artigo: "Art. 7º", texto: "Art. 7º - Esta Lei entra em vigor na data de sua publicação." },
    { ordem: 8, artigo: "Art. 8º", texto: "Art. 8º - Revogam-se as disposições em contrário." },
  ],
};

const EXEMPLO_2026: Lei = {
  id: "exemplo-2026",
  chave: "14320",
  ano: "2026",
  data_lei: "2026-10-20",
  titulo: "LEI Nº 14.320, DE 20 DE OUTUBRO DE 2026",
  ementa: "Dispõe sobre a arborização urbana do Município de Londrina.",
  situacao: "vigente",
  link: "",
  exemplo: true,
  relacoes: [{ tipo: "revoga", id: "exemplo-1980", chave: "3105" }],
  artigos: [
    { ordem: 1, artigo: "Art. 1º", texto: "Art. 1º A poda e o corte de árvores em vias públicas dependem de autorização da Secretaria Municipal do Ambiente." },
    { ordem: 2, artigo: "Art. 2º", texto: "Art. 2º O pedido de autorização poderá ser feito pela internet, no portal da Prefeitura, com prazo de resposta de 15 (quinze) dias." },
    { ordem: 3, artigo: "Art. 3º", texto: "Art. 3º Fica proibido o corte de árvores nativas em terrenos particulares sem licença." },
    { ordem: 4, artigo: "Art. 4º", texto: "Art. 4º O infrator pagará multa de R$ 1.500,00 (mil e quinhentos reais) por árvore cortada, dobrada em caso de reincidência." },
    { ordem: 5, artigo: "Art. 5º", texto: "Art. 5º As árvores plantadas em calçadas deverão ser de espécies nativas da região, conforme lista publicada pela Secretaria Municipal do Ambiente." },
    { ordem: 6, artigo: "Art. 6º", texto: "Art. 6º O Município manterá mapa digital das árvores da cidade, disponível na internet." },
    { ordem: 7, artigo: "Art. 7º", texto: "Art. 7º Ficam protegidas as árvores localizadas em fundos de vale e nascentes." },
    { ordem: 8, artigo: "Art. 8º", texto: "Art. 8º Esta Lei entra em vigor na data de sua publicação." },
    { ordem: 9, artigo: "Art. 9º", texto: "Art. 9º Fica revogada a Lei nº 3.105, de 12 de maio de 1980." },
  ],
};

export const LEIS: Lei[] = [
  EXEMPLO_2026,
  EXEMPLO_1980,
  {
    id: "296902",
    chave: "14294",
    ano: "2026",
    data_lei: "2026-10-29",
    titulo: "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
    ementa: "Institui o Código Ambiental do Município de Londrina.",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902",
    relacoes: [{ tipo: "revoga", id: "35210", chave: "11471" }],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    id: "35210",
    chave: "11471",
    ano: "2012",
    data_lei: null,
    titulo: "LEI ORDINÁRIA Nº 11471/2012",
    ementa: "Institui o Código Ambiental do Município de Londrina.",
    situacao: "revogada",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35210",
    relacoes: [
      { tipo: "alterada_por", id: null, chave: "13529" },
      { tipo: "revogada_por", id: "296902", chave: "14294" },
    ],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    id: "298447",
    chave: "14293",
    ano: "2026",
    data_lei: "2026-10-29",
    titulo: "LEI N.º 14293, DE 29 DE OUTUBRO DE 2026",
    ementa:
      "Dispõe sobre a instalação de câmeras de segurança em fundos de vale do município, visando coibir o descarte irregular de lixo.",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/298447",
    relacoes: [],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    id: "298454",
    chave: "14300",
    ano: "2026",
    data_lei: "2026-11-11",
    titulo: "LEI N.º 14300, DE 11 DE NOVEMBRO DE 2026",
    ementa:
      "Institui o Dia Municipal do Enfermeiro no Calendário de Comemorações Oficiais do Município de Londrina.",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/298454",
    relacoes: [],
    artigos: [
      {
        ordem: 1,
        artigo: "Art. 1º",
        texto:
          "Fica incluído, no Calendário de Comemorações Oficiais do Município de Londrina, o Dia Municipal do Enfermeiro, a ser celebrado anualmente no dia 12 de maio.",
      },
      { ordem: 2, artigo: "Art. 2º", texto: "Esta Lei entra em vigor na data de sua publicação." },
    ],
  },
  {
    id: "297374",
    chave: "14296",
    ano: "2026",
    data_lei: "2026-11-04",
    titulo: "LEI N.º 14296, DE 04 DE NOVEMBRO DE 2026",
    ementa:
      "Dispõe sobre a garantia de recesso escolar aos professores e profissionais do magistério da Rede Municipal de Ensino de Londrina.",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/297374",
    relacoes: [],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    id: "38880",
    chave: "2598",
    ano: "1975",
    data_lei: null,
    titulo: "LEI ORDINÁRIA Nº 2598/1975",
    ementa:
      "Acresce item ao art. 5º da Lei nº 974/65 (dispõe que as rendas provenientes de serviços de natureza industrial prestados pelo Município são considerados preços).",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38880",
    relacoes: [
      { tipo: "altera", id: null, chave: "974" },
      { tipo: "revoga", id: "37367", chave: "963" },
    ],
    artigos: [
      {
        ordem: 1,
        artigo: "Art. 1º",
        texto:
          "O artigo 5º, da Lei Municipal nº 974, de 09 de abril de 1965, fica acrescido de um item com a seguinte redação: \"VIII - Uso da Estação Rodoviária.\"",
      },
      {
        ordem: 2,
        artigo: "Art. 3º",
        texto:
          "É obrigatório o uso da Estação Rodoviária Municipal, como local de chegada e partida de veículos de transporte coletivo de passageiros, exceto os de natureza urbana.",
      },
    ],
  },
  {
    id: "37367",
    chave: "963",
    ano: "1964",
    data_lei: null,
    titulo: "LEI ORDINÁRIA Nº 963/1964",
    ementa:
      "Cria a Taxa de Uso da Estação Rodoviária do Município, que será devida pelos passageiros que a ela se dirijam para fins de embarque.",
    situacao: "revogada",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37367",
    relacoes: [{ tipo: "revogada_por", id: "38880", chave: "2598" }],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    id: "28522",
    chave: "219",
    ano: "1953",
    data_lei: null,
    titulo: "LEI ORDINÁRIA Nº 219/1953",
    ementa: "Institui o Código de Posturas do Município de Londrina.",
    situacao: "revogada",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28522",
    relacoes: [{ tipo: "revogada_por", id: null, chave: "2576" }],
    artigos: [{ ordem: 1, artigo: "Art. 1º", texto: PENDENTE }],
  },
  {
    // Lei e decreto reais: a lei manda regulamentar, o Decreto 466/2025 lista os documentos.
    id: "222659",
    chave: "13898",
    ano: "2024",
    data_lei: "2024-12-19",
    titulo: "LEI N.º 13898, DE 19 DE DEZEMBRO DE 2024",
    ementa: "Dispõe sobre o parcelamento do solo para fins urbanos no Município de Londrina e dá outras providências.",
    situacao: "vigente",
    link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/222659",
    relacoes: [],
    artigos: [
      {
        ordem: 59,
        artigo: "Art. 56",
        texto:
          "Art. 56. Decreto Municipal regulamentará a emissão de Consulta Prévia de Parcelamento do Solo de caráter informativo sobre os parâmetros urbanísticos e a legislação aplicável. Parágrafo único. A Consulta Prévia de Parcelamento do Solo deverá ser expedida no prazo de 60 (sessenta) dias após o cumprimento das exigências legais e terá validade de 180 (cento e oitenta) dias após sua expedição, podendo ser prorrogada por igual período, mediante requerimento do interessado, durante seu prazo de validade.",
      },
    ],
    decretos: [
      {
        id: "decreto-466-2025",
        titulo: "Decreto 466/2025",
        tipo: "Decreto",
        numero: "466",
        ano: 2025,
        ementa: DECRETO_466,
        link: "https://repositorio.londrina.pr.gov.br/index.php/menu-obras/diretoria-de-loteamentos/70387-decreto-466/file",
        situacao: "sem_registro_de_revogacao",
        revogado_por: null,
        texto_disponivel: true,
        vinculo: "regulamentada_por",
        dispositivos: [],
      },
    ],
  },
];

const porId = (id: string) => LEIS.find((l) => l.id === id)!;

function fonte(id: string, artigoOrdem?: number) {
  const l = porId(id);
  const a = artigoOrdem ? l.artigos.find((x) => x.ordem === artigoOrdem) : undefined;
  return {
    lei_id: l.id,
    chave: l.chave,
    ano: l.ano,
    ementa: l.ementa,
    situacao: l.situacao,
    artigo: a?.artigo ?? null,
    trecho: a && a.texto !== PENDENTE ? a.texto : null,
    link: l.link,
  };
}

const RESPOSTAS: { palavras: RegExp; resposta: Resposta }[] = [
  {
    // Mesma resposta que a API monta com a Lei 13.898/2024 e o Decreto 466/2025 (textos reais).
    palavras: /consulta pr[ée]via|parcelamento do solo|loteamento/i,
    resposta: {
      resposta:
        "Segundo a Lei nº 13.898/2024, Art. 56: “Decreto Municipal regulamentará a emissão de Consulta Prévia de Parcelamento do Solo de caráter informativo sobre os parâmetros urbanísticos e a legislação aplicável.”\n\nO Decreto 466/2025, que regulamenta a Lei nº 13.898/2024, detalha no Art. 2º: “Para obtenção da Consulta de Parcelamento do Solo (CPS) o interessado deverá protocolizar requerimento ao Poder Público, anexando os seguintes documentos: I. requerimento por meio de formulário eletrônico disponibilizado no sistema SEI II. croqui de localização do imóvel no bairro ou vizinhança; III. Comprovante do recolhimento de taxa administrativa.”",
      fontes: [fonte("222659", 59)],
      ignoradas: [],
      camadas: [
        {
          papel: "lei",
          descricao: "Lei que traz a regra",
          titulo: "Lei 13.898/2024",
          lei_id: "222659",
          link: "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/222659",
          ementa: "Dispõe sobre o parcelamento do solo para fins urbanos no Município de Londrina e dá outras providências.",
          situacao: "vigente",
          artigo: "Art. 56",
          trecho:
            "Art. 56. Decreto Municipal regulamentará a emissão de Consulta Prévia de Parcelamento do Solo de caráter informativo sobre os parâmetros urbanísticos e a legislação aplicável.",
          texto_na_base: true,
        },
        {
          papel: "regulamentada_por",
          descricao: "Decreto que detalha como aplicar a lei",
          titulo: "Decreto 466/2025",
          decreto_id: "decreto-466-2025",
          link: "https://repositorio.londrina.pr.gov.br/index.php/menu-obras/diretoria-de-loteamentos/70387-decreto-466/file",
          ementa: DECRETO_466,
          situacao: "sem_registro_de_revogacao",
          artigo: "Art. 2º",
          trecho:
            "Art. 2º. Para obtenção da Consulta de Parcelamento do Solo (CPS) o interessado deverá protocolizar requerimento ao Poder Público, anexando os seguintes documentos: I. requerimento por meio de formulário eletrônico disponibilizado no sistema SEI II. croqui de localização do imóvel no bairro ou vizinhança; III. Comprovante do recolhimento de taxa administrativa.",
          texto_na_base: true,
        },
      ],
      alertas: [],
    },
  },
  {
    palavras: /árvore|arvore|poda|podar|corte de/i,
    resposta: {
      resposta:
        "Para podar ou cortar uma árvore na calçada, é preciso pedir autorização à Secretaria Municipal do Ambiente. O pedido pode ser feito pela internet e a resposta sai em até 15 dias. Quem corta sem autorização paga multa de R$ 1.500,00 por árvore. (Lei de exemplo, para demonstração.)",
      fontes: [fonte("exemplo-2026", 1), fonte("exemplo-2026", 4)],
      ignoradas: [
        { lei_id: "exemplo-1980", chave: "3105", ano: "1980", motivo: "Revogada pela Lei 14.320/2026", revogada_por_id: "exemplo-2026" },
      ],
    },
  },
  {
    palavras: /ambient|árvore|arvore|natureza|meio ambiente|poda|vegeta/i,
    resposta: {
      resposta:
        "As regras ambientais de Londrina estão no novo Código Ambiental, a Lei 14.294, de 29 de outubro de 2026. Ela substituiu por inteiro o Código Ambiental de 2012, que não vale mais.",
      fontes: [fonte("296902")],
      ignoradas: [{ lei_id: "35210", chave: "11471", ano: "2012", motivo: "Revogada pela Lei 14.294/2026" }],
    },
  },
  {
    palavras: /lixo|entulho|descarte|fundo de vale|câmera|camera/i,
    resposta: {
      resposta:
        "A Lei 14.293, de 29 de outubro de 2026, prevê câmeras de segurança nos fundos de vale de Londrina para coibir o descarte irregular de lixo.",
      fontes: [fonte("298447")],
      ignoradas: [],
    },
  },
  {
    palavras: /enferm/i,
    resposta: {
      resposta: "O Dia Municipal do Enfermeiro é comemorado todo ano em 12 de maio, conforme a Lei 14.300, de 2026.",
      fontes: [fonte("298454", 1)],
      ignoradas: [],
    },
  },
  {
    palavras: /rodovi|ônibus|onibus|embarque|passagei/i,
    resposta: {
      resposta:
        "A Lei 2.598, de 1975, torna obrigatório o uso da Estação Rodoviária Municipal para a chegada e a partida do transporte coletivo de passageiros, exceto o urbano. A antiga taxa de uso da rodoviária, de 1964, foi revogada por essa lei.",
      fontes: [fonte("38880", 2)],
      ignoradas: [{ lei_id: "37367", chave: "963", ano: "1964", motivo: "Revogada pela Lei 2.598/1975" }],
    },
  },
  {
    palavras: /professor|escola|recesso|magist/i,
    resposta: {
      resposta:
        "A Lei 14.296, de 4 de novembro de 2026, garante recesso escolar aos professores e profissionais do magistério da Rede Municipal de Ensino de Londrina.",
      fontes: [fonte("297374")],
      ignoradas: [],
    },
  },
];

export function respostaExemplo(pergunta: string): Resposta {
  const achou = RESPOSTAS.find((r) => r.palavras.test(pergunta));
  if (achou) return achou.resposta;
  return {
    resposta:
      "Não encontrei uma lei sobre esse assunto nos dados de exemplo. Tente perguntar sobre meio ambiente, descarte de lixo, rodoviária ou recesso escolar.",
    fontes: [],
    ignoradas: [],
  };
}
