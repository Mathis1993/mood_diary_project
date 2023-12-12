// Base Service Worker implementation taken from django-pwa (https://github.com/silviolleite/django-pwa).

var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = [
    '/offline/',
    'static/theme/vendor/fontawesome-free/css/all.min.css',
    'static/theme/vendor/fontawesome-free/css/fontawesome.min.css',
    'https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i',
    'static/theme/css/sb-admin-2.min.css',
    'static/css/styles.css',
    'static/images/icons/favicon.ico',
    'static/theme/img/undraw_profile.svg',
    'static/theme/vendor/fontawesome-free/webfonts/fa-solid-900.woff',
    'static/theme/vendor/fontawesome-free/webfonts/fa-solid-900.woff2',
    'static/theme/vendor/fontawesome-free/webfonts/fa-solid-900.ttf',
    '/static/images/icons/android-chrome-512x512.png',
    '/static/images/icons/apple-touch-icon.png',
    '/static/images/splash_screens/iPhone_14_Pro_Max_landscape.png',
    '/static/images/splash_screens/iPhone_14_Pro_landscape.png',
    '/static/images/splash_screens/iPhone_14_Plus__iPhone_13_Pro_Max__iPhone_12_Pro_Max_landscape.png',
    '/static/images/splash_screens/iPhone_14__iPhone_13_Pro__iPhone_13__iPhone_12_Pro__iPhone_12_landscape.png',
    '/static/images/splash_screens/iPhone_13_mini__iPhone_12_mini__iPhone_11_Pro__iPhone_XS__iPhone_X_landscape.png',
    '/static/images/splash_screens/iPhone_11_Pro_Max__iPhone_XS_Max_landscape.png',
    '/static/images/splash_screens/iPhone_11__iPhone_XR_landscape.png',
    '/static/images/splash_screens/iPhone_8_Plus__iPhone_7_Plus__iPhone_6s_Plus__iPhone_6_Plus_landscape.png',
    '/static/images/splash_screens/iPhone_8__iPhone_7__iPhone_6s__iPhone_6__4.7__iPhone_SE_landscape.png',
    '/static/images/splash_screens/4__iPhone_SE__iPod_touch_5th_generation_and_later_landscape.png',
    '/static/images/splash_screens/12.9__iPad_Pro_landscape.png',
    '/static/images/splash_screens/11__iPad_Pro__10.5__iPad_Pro_landscape.png',
    '/static/images/splash_screens/10.9__iPad_Air_landscape.png',
    '/static/images/splash_screens/10.5__iPad_Air_landscape.png',
    '/static/images/splash_screens/10.2__iPad_landscape.png',
    '/static/images/splash_screens/9.7__iPad_Pro__7.9__iPad_mini__9.7__iPad_Air__9.7__iPad_landscape.png',
    '/static/images/splash_screens/8.3__iPad_Mini_landscape.png',
    '/static/images/splash_screens/iPhone_14_Pro_Max_portrait.png',
    '/static/images/splash_screens/iPhone_14_Pro_portrait.png',
    '/static/images/splash_screens/iPhone_14_Plus__iPhone_13_Pro_Max__iPhone_12_Pro_Max_portrait.png',
    '/static/images/splash_screens/iPhone_14__iPhone_13_Pro__iPhone_13__iPhone_12_Pro__iPhone_12_portrait.png',
    '/static/images/splash_screens/iPhone_13_mini__iPhone_12_mini__iPhone_11_Pro__iPhone_XS__iPhone_X_portrait.png',
    '/static/images/splash_screens/iPhone_11_Pro_Max__iPhone_XS_Max_portrait.png',
    '/static/images/splash_screens/iPhone_11__iPhone_XR_portrait.png',
    '/static/images/splash_screens/iPhone_8_Plus__iPhone_7_Plus__iPhone_6s_Plus__iPhone_6_Plus_portrait.png',
    '/static/images/splash_screens/iPhone_8__iPhone_7__iPhone_6s__iPhone_6__4.7__iPhone_SE_portrait.png',
    '/static/images/splash_screens/4__iPhone_SE__iPod_touch_5th_generation_and_later_portrait.png',
    '/static/images/splash_screens/12.9__iPad_Pro_portrait.png',
    '/static/images/splash_screens/11__iPad_Pro__10.5__iPad_Pro_portrait.png',
    '/static/images/splash_screens/10.9__iPad_Air_portrait.png',
    '/static/images/splash_screens/10.2__iPad_portrait.png',
    '/static/images/splash_screens/10.5__iPad_Air_portrait.png',
    '/static/images/splash_screens/9.7__iPad_Pro__7.9__iPad_mini__9.7__iPad_Air__9.7__iPad_portrait.png',
    '/static/images/splash_screens/8.3__iPad_Mini_portrait.png',
];

// Cache on install.
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            }).catch((err) => {
            console.error('Caching caused an error: ', err);
        })
    )
});

// Clear cache on activate.
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
    if (Notification.permission === 'granted') {
        // Send message to main thread to update the push subscription
        self.clients.matchAll().then(clients => {
            console.log('Sending update message')
            clients.forEach(client => client.postMessage('update-push-subscription'));
        });
    }
});

// Serve from Cache.
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

// Handle incoming push events.
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

// Listen for push events.
self.addEventListener('push', function (event) {
    event.waitUntil(handlePushEvent(event));
});

// Listen for notification click events.
self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
