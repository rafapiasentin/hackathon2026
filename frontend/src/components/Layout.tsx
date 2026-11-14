import { motion } from "motion/react";
import { Scale } from "lucide-react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { MODO_EXEMPLO } from "../api/client";
import { BarraAcessibilidade } from "./BarraAcessibilidade";

const link = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-[0.95rem] font-medium transition ${
    isActive ? "bg-primary-soft text-primary-strong" : "text-muted hover:text-text"
  }`;

export function Layout() {
  const { pathname } = useLocation();

  // Ao trocar de página, leva o foco ao conteúdo (bom para leitor de tela)
  useEffect(() => {
    window.scrollTo(0, 0);
    document.getElementById("conteudo")?.focus({ preventScroll: true });
  }, [pathname]);

  return (
    <div className="flex min-h-screen flex-col">
      <BarraAcessibilidade />

      <header className="border-b border-border bg-surface/90 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <NavLink to="/inicio" className="flex items-center gap-2.5 rounded-lg" aria-label="Londrina Conecta, página inicial">
            <span className="grid size-9 place-items-center rounded-xl bg-primary text-on-primary">
              <Scale aria-hidden="true" className="size-5" />
            </span>
            <span className="leading-tight">
              <span className="block font-bold tracking-tight">Londrina Conecta</span>
              <span className="block text-xs text-muted">Leis de Londrina, em linguagem simples</span>
            </span>
          </NavLink>
          <nav aria-label="Menu principal" className="flex gap-1">
            <NavLink to="/inicio" end className={link}>
              Perguntar
            </NavLink>
            <NavLink to="/leis" className={link}>
              Buscar leis
            </NavLink>
            <NavLink to="/validador" className={link}>
              Validar lei
            </NavLink>
          </nav>
        </div>
      </header>

      {MODO_EXEMPLO && (
        <div className="border-b border-warn/30 bg-warn-soft text-warn">
          <p className="mx-auto max-w-5xl px-4 py-1.5 text-center text-sm font-medium sm:px-6">
            Modo demonstração: usando dados de exemplo. Ligue o backend em <code>VITE_API_URL</code> para usar todas as leis.
          </p>
        </div>
      )}

      <main id="conteudo" tabIndex={-1} className="flex-1 focus:outline-none">
        {/* Troca de página: só opacidade (deslocar com transform quebraria as barras fixas da conversa) */}
        <motion.div key={pathname} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.25, ease: "easeOut" }}>
          <Outlet />
        </motion.div>
      </main>

      <footer id="rodape" tabIndex={-1} className="border-t border-border bg-surface">
        <div className="mx-auto grid max-w-5xl gap-2 px-4 py-6 text-sm text-muted sm:px-6">
          <p>
            As respostas são geradas com base nas leis publicadas pela{" "}
            <a className="text-primary underline-offset-4 hover:underline" href="https://www.cml.pr.gov.br" target="_blank" rel="noreferrer">
              Câmara Municipal de Londrina
            </a>
            . Elas não substituem a orientação de um advogado ou da prefeitura.
          </p>
          <p>Projeto do Hackathon Smart Cities Londrina 2026.</p>
        </div>
      </footer>
    </div>
  );
}
