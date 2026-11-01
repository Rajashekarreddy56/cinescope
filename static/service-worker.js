'use strict';
const VERSION = 'cinescope-pwa-v2';
const SHELL_CACHE = `${VERSION}-shell`;
const DATA_CACHE = `${VERSION}-data`;
const IMAGE_CACHE = `${VERSION}-images`;
const SHELL_URLS = [
  '/',
  '/static/styles.css',
  '/static/app.js',
  '/static/manifest.webmanifest',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL_CACHE);
    await cache.addAll(SHELL_URLS);
    // Warm the default catalogue so the first successful visit can be reopened offline.
    const data = await caches.open(DATA_CACHE);
    await Promise.allSettled([
      '/api/status',
      '/api/movies?industry=all&category=popular&page=1&q='
    ].map(async (url) => {
      const response = await fetch(url);
      if (response.ok) await data.put(url, response.clone());
    }));
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((key) => key.startsWith('cinescope-') && ![SHELL_CACHE, DATA_CACHE, IMAGE_CACHE].includes(key)).map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(request);
    if (response && response.ok) { cache.put(request, response.clone()).catch(() => {}); return response; }
    const cached = await cache.match(request);
    return cached || response;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw error;
  }
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin && !url.hostname.endsWith('.tmdb.org')) return;

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        const cache = await caches.open(SHELL_CACHE);
        cache.put('/', response.clone()).catch(() => {});
        return response;
      } catch (_) {
        return (await caches.match('/')) || new Response('CineScope is offline and the app shell is not cached yet. Reconnect once to prepare offline access.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
      }
    })());
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, DATA_CACHE));
    return;
  }

  if (url.hostname.endsWith('.tmdb.org')) {
    event.respondWith((async () => {
      const cache = await caches.open(IMAGE_CACHE);
      const cached = await cache.match(request);
      if (cached) return cached;
      try {
        const response = await fetch(request);
        if (response.ok || response.type === 'opaque') cache.put(request, response.clone()).catch(() => {});
        return response;
      } catch (error) { throw error; }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    const response = await fetch(request);
    if (response.ok) (await caches.open(SHELL_CACHE)).put(request, response.clone()).catch(() => {});
    return response;
  })());
});
