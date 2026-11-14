// Compatibilidade com Pages configurado em main / (sem acesso administrativo).
import { cpSync, existsSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const dist = join(raiz, 'frontend', 'dist');
if (!existsSync(join(dist, 'index.html'))) throw new Error('Gere antes: npm run build -- --mode pages');
for (const item of ['index.html', 'assets', 'exemplos', 'favicon.svg']) {
  if (existsSync(join(dist, item))) cpSync(join(dist, item), join(raiz, item), { recursive: true });
}
writeFileSync(join(raiz, '.nojekyll'), '');
console.log('Front exportado para main /, origem ativa do GitHub Pages.');
