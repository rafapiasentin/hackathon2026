import { Contrast, HandHelping } from "lucide-react";
import { useAcessibilidade } from "../lib/acessibilidade";

/** Barra no topo, no padrão dos sites do governo: atalhos, alto contraste, tamanho da letra e Libras. */
export function BarraAcessibilidade() {
  const a = useAcessibilidade();
  const botao =
    "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-sm font-medium text-primary-strong hover:bg-primary-soft aria-pressed:bg-primary aria-pressed:text-on-primary";

  return (
    <div className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-4 gap-y-1 px-4 py-1.5 sm:px-6">
        <nav aria-label="Atalhos de teclado" className="flex flex-wrap gap-x-3 text-sm">
          <a className="rounded px-1 text-primary-strong underline-offset-4 hover:underline" href="#conteudo" accessKey="1">
            Ir para o conteúdo <kbd className="font-sans text-muted">[1]</kbd>
          </a>
          <a className="rounded px-1 text-primary-strong underline-offset-4 hover:underline" href="#busca" accessKey="2">
            Ir para a busca <kbd className="font-sans text-muted">[2]</kbd>
          </a>
          <a className="rounded px-1 text-primary-strong underline-offset-4 hover:underline" href="#rodape" accessKey="3">
            Ir para o rodapé <kbd className="font-sans text-muted">[3]</kbd>
          </a>
        </nav>

        <div className="flex items-center gap-1" role="group" aria-label="Opções de acessibilidade">
          <button type="button" className={botao} aria-pressed={a.contraste} onClick={a.alternarContraste}>
            <Contrast aria-hidden="true" className="size-4" />
            Alto contraste
          </button>
          <button
            type="button"
            className={botao}
            onClick={a.diminuir}
            disabled={a.fonte === 0}
            aria-label="Diminuir o tamanho da letra"
          >
            A−
          </button>
          <button
            type="button"
            className={`${botao} text-base`}
            onClick={a.aumentar}
            disabled={a.fonte === 3}
            aria-label="Aumentar o tamanho da letra"
          >
            A+
          </button>
          <span className="sr-only" aria-live="polite">
            {a.fonte ? `Letra aumentada, nível ${a.fonte} de 3` : ""}
          </span>
          <span className="hidden items-center gap-1.5 px-2 text-sm text-muted md:inline-flex">
            <HandHelping aria-hidden="true" className="size-4" />
            Libras: botão azul à direita
          </span>
        </div>
      </div>
    </div>
  );
}
