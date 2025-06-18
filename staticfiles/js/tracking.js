let lastPingTime = Date.now();
let isPollingActive = true;

function trackPageVisit(useBeacon = false) {
    const consent = getCookieConsent();
    if (!(consent && consent.analytics)) return;

    const data = { country: detectedCountry || 'Unknown' };
    const url = "{% url 'track_page_visit' %}";

    if (useBeacon && navigator.sendBeacon) {
        navigator.sendBeacon(url, new Blob([JSON.stringify(data)], { type: 'application/json' }));
    } else {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify(data)
        });
    }
}

function detectCountry() {
    fetch("https://ipapi.co/json/")
        .then(response => response.json())
        .then(data => {
            detectedCountry = data.country_name || 'Unknown';
            trackPageVisit();
        })
        .catch(() => {
            detectedCountry = 'Unknown';
            trackPageVisit();
        });
}

document.addEventListener('DOMContentLoaded', () => {
    detectCountry();
    setInterval(() => trackPageVisit(), 30000);
});

window.addEventListener('beforeunload', () => {
    isPollingActive = false;
    clearInterval(countdownInterval);
    trackPageVisit(true);
});

document.addEventListener('mousemove', () => lastPingTime = Date.now());
document.addEventListener('keypress', () => lastPingTime = Date.now());
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        trackPageVisit();
    }
});
