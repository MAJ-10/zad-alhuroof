/* زاد الحروف — عامل الخدمة: يخزّن الموقع ليعمل بلا إنترنت.
   السطر التالي يحدّثه build.py من بصمة index.html، فكل تعديل على
   الأسئلة يصنع مخزناً جديداً ويمسح القديم. لا تعدّله يدوياً. */
const VERSION = 'b7732575afb7';                       /* ══ بصمة البناء ══ */

const CACHE = 'zad-alhuroof-' + VERSION;
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './icon-180.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== location.origin) return;

  /* فتح الموقع: جرّب الشبكة أولاً ليصل أي تحديث، وإلا فمن المخزن */
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put('./index.html', copy));
          return res;
        })
        .catch(() => caches.match('./index.html').then(r => r || caches.match('./')))
    );
    return;
  }

  /* بقية الملفات: من المخزن فوراً، ومن الشبكة إن لم تكن مخزَّنة */
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
      }
      return res;
    }))
  );
});
