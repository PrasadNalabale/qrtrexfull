const CACHE_NAME = "qr-menu-cache-v2";
const urlsToCache = [

  "/static/qr/css/cart.css",
  "/static/qr/css/main.css",
  "/static/qr/css/qr-menu.css",
  "/static/qr/css/starability-all.css",
  "/static/qr/js/main.js",
  "/static/qr/js/menu.js",
  "/static/qr/js/qrMenu.js",
  "/static/qr/js/search.js",
  "/static/qr/js/cart.js",
  "/static/qr/images/logo.jpeg"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      )
    )
  );
});