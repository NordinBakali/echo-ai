function isSameOriginGetRequest(request) {
  if (!request || request.method !== 'GET') {
    return false;
  }

  const requestUrl = new URL(request.url);
  return requestUrl.origin === self.location.origin;
}

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  if (!isSameOriginGetRequest(event.request)) {
    return;
  }

  event.respondWith(
    fetch(event.request, { cache: 'no-store' }).catch(() => Response.error())
  );
});
