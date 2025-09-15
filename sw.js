// sw.js
const VERSION = 'v1.0.1';
const CACHE_NAME = `cadastro-produtor-rural-${VERSION}`;
const BASE = self.location.pathname.replace(/\/[^\/]*$/, '');

// Use caminhos RELATIVOS ao escopo do SW e normalize para URL absoluta com base no escopo
const PRECACHE_PATHS = [
  `${BASE}/`,
  `${BASE}/index.html`,
  `${BASE}/manifest.webmanifest`,
  `${BASE}/static/icon.png`,
  `${BASE}/static/css/bootstrap.min.css`,
  `${BASE}/static/css/bootstrap-icons.css`,
  `${BASE}/static/js/bootstrap.bundle.min.js`,
  `${BASE}/static/js/alpine.min.js`,
  `${BASE}/static/js/jszip.min.js`,
  `${BASE}/static/fonts/bootstrap-icons.woff2`,
  `${BASE}/static/fonts/bootstrap-icons.woff`
];
const ASSETS = PRECACHE_PATHS.map(p => new URL(p, self.registration.scope).toString());

// INSTALAR: pré-cache (falha de 1 arquivo derruba a instalação, então logue erros)
self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    try {
      await cache.addAll(ASSETS);
      console.log('[SW] Precache ok', ASSETS);
    } catch (err) {
      console.error('[SW] Precache falhou:', err);
    }
    await self.skipWaiting();
  })());
});

// ATIVAR: limpa versões antigas e assume controle
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => k !== CACHE_NAME && caches.delete(k)));
    await self.clients.claim();
  })());
});

// FETCH:
// - Navegações: network-first, fallback para index.html do escopo
// - Estáticos do mesmo host: cache-first, gravando no cache quando vier da rede
// - ignoreSearch ajuda com arquivos que vêm com ?v= (ex.: fontes do bootstrap-icons)
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Navegação (abrindo app PWA / digitando URL)
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        return await fetch(req);
      } catch {
        const fallback = await caches.match(new URL('./index.html', self.registration.scope).toString());
        return fallback || Response.error();
      }
    })());
    return;
  }

  // Mesma origem: cache-first
  if (url.origin === self.location.origin) {
    event.respondWith((async () => {
      const cached = await caches.match(req, { ignoreSearch: true });
      if (cached) return cached;

      try {
        const fresh = await fetch(req);
        const cache = await caches.open(CACHE_NAME);
        cache.put(req, fresh.clone());
        return fresh;
      } catch {
        return Response.error();
      }
    })());
  }
});

// (Opcional) Background Sync placeholder
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-produtores') {
    event.waitUntil((async () => {
      console.log('Tentativa de sincronização background');
    })());
  }
});
