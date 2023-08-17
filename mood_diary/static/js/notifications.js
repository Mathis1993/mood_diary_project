// ToDo: Add function to create and send subscription object to server every time the app is accessed and have it called accordingly

function requestNotificationPermission() {
    if ('Notification' in window && navigator.serviceWorker) {
        let permissionStatus;
        Notification.requestPermission().then(function (permission) {
            if (permission === 'granted') {
                console.log('Notification permission granted.');
                permissionStatus = 'granted';
                subscribeUserToPush();
            } else {
                console.log('Notification permission denied.');
                permissionStatus = 'denied';
            }

            // Make an AJAX request to update the client model
            fetch('/notifications/update_notifications_permission/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Fetch the CSRF token
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({permission: permissionStatus})
            }).then(response => {
                if (response.ok) {
                    // Refresh the page to update the UI
                    location.reload();
                }
            });
        });
    } else {
        console.log('This browser does not support notifications.');
    }
}

// Regularly update the push subscription (upon service worker activation)
navigator.serviceWorker.addEventListener('message', event => {
    console.log("Message received from service worker: ", event.data);
    if (event.data === 'update-push-subscription') {
        // Update the push subscription
        subscribeUserToPush();
    }
});

// Helper function to subscribe the user to push notifications
function subscribeUserToPush() {
    console.log('Subscribing user to push notifications...')
    navigator.serviceWorker.ready.then(function (registration) {
        registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array('BKq9sY0dNJzVKyg6PmJm57oMwNBDgEYZGtrUjsA59DmImGOX-GmFtcMekXWxQQShePZDGHdyPILpbL7Aoh3V5v4')
        }).then(function (subscription) {
            // Send the subscription object to the server
            fetch('/notifications/push_subscriptions/create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscription)
            });
        }).catch(function (error) {
            console.error('Failed to subscribe the user: ', error);
        });
    });
}

// Helper function to convert a base64 string to a Uint8Array (as expected for the VAPID key)
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Helper function to get a cookie by name
function getCookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}
