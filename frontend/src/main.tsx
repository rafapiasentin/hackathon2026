import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, HashRouter, Route, Routes } from "react-router-dom";
import { MotionConfig } from "motion/react";
import "./index.css";
import { Layout } from "./components/Layout";
import { Inicio } from "./pages/Inicio";
import { Conversa } from "./pages/Conversa";
import { Lei } from "./pages/Lei";
import { Busca } from "./pages/Busca";
import { Validador } from "./pages/Validador";
import { Comparar } from "./pages/Comparar";
import { CamaraLayout } from "./camara/CamaraLayout";
import { CamaraInicio } from "./camara/CamaraInicio";

const Router = import.meta.env.MODE === "pages" ? HashRouter : BrowserRouter;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* reducedMotion="user": quem pediu menos movimento no sistema não vê animações */}
    <MotionConfig reducedMotion="user">
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Inicio />} />
            <Route path="perguntar" element={<Conversa />} />
            <Route path="leis" element={<Busca />} />
            <Route path="lei/:id" element={<Lei />} />
            <Route path="validador" element={<Validador />} />
            <Route path="comparar" element={<Comparar />} />
            <Route path="comparar/:antiga/:nova" element={<Comparar />} />
            <Route path="*" element={<Inicio />} />
          </Route>
          {/* Demonstração: as mesmas telas dentro de uma réplica do site da Câmara */}
          <Route path="camara" element={<CamaraLayout />}>
            <Route index element={<CamaraInicio />} />
            <Route path="consulta" element={<Inicio />} />
            <Route path="perguntar" element={<Conversa />} />
            <Route path="leis" element={<Busca />} />
            <Route path="lei/:id" element={<Lei />} />
            <Route path="validador" element={<Validador />} />
            <Route path="comparar" element={<Comparar />} />
            <Route path="comparar/:antiga/:nova" element={<Comparar />} />
          </Route>
        </Routes>
      </Router>
    </MotionConfig>
  </StrictMode>,
);
