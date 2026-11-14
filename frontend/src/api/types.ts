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

export interface Lei extends LeiResumo {
  relacoes: Relacao[];
  artigos: Artigo[];
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

export interface Resposta {
  resposta: string;
  fontes: Fonte[];
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
