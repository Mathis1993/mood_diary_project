// Base Service Worker implementation taken from django-pwa (https://github.com/silviolleite/django-pwa)

var staticCacheName = "django-pwa-v" + new Date().getTime();
// ToDo: Update the files to cache
var filesToCache = [
    '/offline/',
    '/static/css/django-pwa-app.css',
    '/static/images/icons/icon-72x72.png',
    '/static/images/icons/icon-96x96.png',
    '/static/images/icons/icon-128x128.png',
    '/static/images/icons/icon-144x144.png',
    '/static/images/icons/icon-152x152.png',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-384x384.png',
    '/static/images/icons/icon-512x512.png',
    '/static/images/icons/splash-640x1136.png',
    '/static/images/icons/splash-750x1334.png',
    '/static/images/icons/splash-1242x2208.png',
    '/static/images/icons/splash-1125x2436.png',
    '/static/images/icons/splash-828x1792.png',
    '/static/images/icons/splash-1242x2688.png',
    '/static/images/icons/splash-1536x2048.png',
    '/static/images/icons/splash-1668x2224.png',
    '/static/images/icons/splash-1668x2388.png',
    '/static/images/icons/splash-2048x2732.png'
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("django-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
    // Update the push subscription upon service worker activation
    if(Notification.permission === 'granted') {
        // Send message to main thread to update the push subscription
        self.clients.matchAll().then(clients => {
            console.log('Sending update message')
            clients.forEach(client => client.postMessage('update-push-subscription'));
        });
    }
});

// Serve from Cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
            .catch(() => {
                return caches.match('/offline/');
            })
    )
});

// Handle incoming push events
function handlePushEvent(event) {
    console.log(event);
    return Promise.resolve()
        .then(() => {
            return event.data.json();
        })
        .then((data) => {
            console.log(data);
            const title = data.title;
            const text = data.text;
            const url = data.url;
            const notificationOptions = {
                body: text,
                icon: 'static/images/icons/android-chrome-512x512.png',
                badge: 'static/images/icons/android-chrome-192x192.png',
                data: {
                    url: url
                }
            };
            return registration.showNotification(title, notificationOptions);
        })
        .catch((err) => {
            console.error('Push event caused an error: ', err);
        });
}

self.addEventListener('push', function (event) {
    event.waitUntil(handlePushEvent(event));
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
