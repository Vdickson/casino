function getCookieConsent() {
    return JSON.parse(localStorage.getItem('cookie_consent'));
}

function saveCookieConsent(analytics, preferences, marketing) {
    const consent = { analytics, preferences, marketing, timestamp: new Date().toISOString(), version: '1.0' };
    localStorage.setItem('cookie_consent', JSON.stringify(consent));
    document.getElementById('cookie-consent-banner').style.display = 'none';
    document.getElementById('cookie-modal').style.display = 'none';
    sendConsentToServer(analytics, preferences, marketing);
    applyUserPreferences();
}

function sendConsentToServer(analytics, preferences, marketing) {
    fetch("{% url 'cookie_consent' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ analytics, preferences, marketing })
    }).catch(console.error);
}

function getCsrfToken() {
    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : '';
}

function setupCookieListeners() {
    document.getElementById('cookie-accept')?.addEventListener('click', () => saveCookieConsent(true, true, true));
    document.getElementById('cookie-reject')?.addEventListener('click', () => saveCookieConsent(false, false, false));
    document.getElementById('cookie-settings')?.addEventListener('click', () => {
        const consent = getCookieConsent() || {};
        document.getElementById('analytics-toggle').checked = consent.analytics || false;
        document.getElementById('preferences-toggle').checked = consent.preferences || false;
        document.getElementById('marketing-toggle').checked = consent.marketing || false;
        document.getElementById('cookie-modal').style.display = 'flex';
    });

    document.getElementById('save-preferences')?.addEventListener('click', () => {
        saveCookieConsent(
            document.getElementById('analytics-toggle').checked,
            document.getElementById('preferences-toggle').checked,
            document.getElementById('marketing-toggle').checked
        );
    });

    document.getElementById('cookie-modal')?.addEventListener('click', e => {
        if (e.target === document.getElementById('cookie-modal')) {
            document.getElementById('cookie-modal').style.display = 'none';
        }
    });

    document.getElementById('cookie-modal-close')?.addEventListener('click', () => {
        document.getElementById('cookie-modal').style.display = 'none';
    });
}

function applyUserPreferences() {
    const consent = getCookieConsent() || {};
    // Disable analytics here if needed
}

document.addEventListener('DOMContentLoaded', () => {
    setupCookieListeners();
    applyUserPreferences();
    if (!getCookieConsent()) {
        document.getElementById('cookie-consent-banner').style.display = 'block';
    }
});
