self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  // Simple pass-through fetch handler required for PWA installation
  event.respondWith(fetch(event.request));
});