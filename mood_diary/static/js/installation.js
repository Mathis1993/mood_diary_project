let deferredPrompt;

// Listen for beforeinstallprompt event fired by the browser.
window.addEventListener('beforeinstallprompt', (e) => {
    console.log("beforeinstallprompt fired");
    deferredPrompt = e;
});

// Display the installation prompt when the user clicks appropriate button.
// This requires that the browser fired the beforeinstallprompt event so that
// event listener above could capture it and store it in the deferredPrompt variable.
function installApp() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      deferredPrompt = null;
    });
  }
}
