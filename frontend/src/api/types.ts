// Tipos que espelham o leis.json gerado pelo coleta_leis.py (ver README da raiz).

export type Situacao = "vigente" | "vigente_com_alteracoes" | "revogada" | "inexistente";

export type TipoRelacao = "altera" | "alterada_por" | "revoga" | "revogada_por";

export interface Relacao {
  tipo: TipoRelacao;
  id: string | null; // null quando a lei citada não está na base
  chave: string;
}

export interface Artigo {
  ordem: number;
  artigo: string;
  texto: string;
  texto_riscado?: string | null;
  revogado?: boolean;
}

export interface LeiResumo {
  id: string;
  chave: string;
  ano: string;
  data_lei: string | null;
  titulo: string;
  ementa: string | null;
  situacao: Situacao;
  link: string;
  exemplo?: boolean;
  vigencia_verificada?: boolean;
}

export type TipoVinculoDecreto = "regulamentada_por" | "anexo_atualizado_por" | "eficacia_suspensa_por";

/** Decreto ligado a uma lei: do prefeito (regulamenta) ou legislativo, da Câmara (pode suspender a eficácia). */
export interface DecretoDaLei {
  id: string;
  titulo: string; // "Decreto 466/2025"
  tipo: "Decreto" | "Decreto Legislativo";
  numero: string;
  ano: number;
  ementa: string | null;
  link: string | null;
  situacao: "revogado" | "sem_registro_de_revogacao";
  revogado_por: string | null;
  texto_disponivel: boolean;
  vinculo: TipoVinculoDecreto;
  /** Artigos da lei em que a Câmara anotou o decreto. Vazio = a lei como um todo. */
  dispositivos: string[];
}

export interface Lei extends LeiResumo {
  relacoes: Relacao[];
  artigos: Artigo[];
  decretos?: DecretoDaLei[];
  /** Só nos dados de demonstração: lei inventada para mostrar uma função. Não existe no site da Câmara. */
  exemplo?: boolean;
}

export interface ResultadoBusca {
  total: number;
  pagina: number;
  itens: LeiResumo[];
}

/** Trecho de lei usado pela IA para responder. */
export interface Fonte {
  lei_id: string;
  chave: string;
  ano: string;
  ementa: string | null;
  situacao: Situacao;
  artigo: string | null;
  trecho: string | null;
  link: string;
}

/** Uma norma na cadeia da resposta: a lei, a lei que mudou o artigo, o decreto que detalha. */
export interface Camada {
  papel: "lei" | "alteracao" | TipoVinculoDecreto;
  /** Papel em linguagem simples: "Decreto que detalha como aplicar a lei". */
  descricao: string;
  titulo: string;
  lei_id?: string | null;
  decreto_id?: string | null;
  link?: string | null;
  ementa?: string | null;
  situacao?: string | null;
  artigo?: string | null;
  trecho?: string | null;
  dispositivo?: string | null;
  /** false quando só sabemos que o decreto existe (a Câmara cita), mas o texto não está na base. */
  texto_na_base: boolean;
}

export interface Resposta {
  resposta: string;
  fontes: Fonte[];
  /** Cadeia de normas por trás da resposta, para o botão "Ver de onde vem". */
  camadas?: Camada[];
  /** Avisos curtos: decreto fora da base, eficácia suspensa, regulamentação pendente. */
  alertas?: string[];
  /** Leis revogadas que tratavam do assunto e foram deixadas de fora. */
  ignoradas: {
    lei_id: string | null;
    chave: string;
    ano: string;
    motivo: string;
    /** id da lei que substituiu esta (para o link "Ver o que mudou"). Opcional. */
    revogada_por_id?: string | null;
  }[];
}
