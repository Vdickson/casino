  </script>
        <script>
    // Add this function to refresh buttons every second
    function refreshButtons() {
        // Clone and replace buttons to reset their state
        document.querySelectorAll('.claim-offer-btn, .game-action-btn, .contact-for-game').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });

        // Reattach event listeners to the new buttons
        attachButtonListeners();
    }

    // Function to reattach event listeners
    function attachButtonListeners() {
        // Claim Offer Buttons
        document.querySelectorAll('.claim-offer-btn').forEach(button => {
            button.addEventListener('click', function() {
                const title = this.getAttribute('data-offer-title');
                const desc = this.getAttribute('data-offer-desc');
                openContactModal(title, desc);
            });
        });

        // Game Footer Buttons
        document.querySelectorAll('.contact-for-game').forEach(button => {
            button.addEventListener('click', function() {
                const gameName = this.getAttribute('data-game-name');
                openContactModal(`Play ${gameName}`, `Ready to play ${gameName}? Contact us to get started!`);
            });
        });

        // Hero Play Now Button
        const heroBtn = document.querySelector('.hero-section .btn-light');
        if (heroBtn) {
            heroBtn.addEventListener('click', function(e) {
                e.preventDefault();
                openContactModal('Get Started', 'Ready to play? Contact us to get started with your account!');
            });
        }
    }

    // Cookie Consent Functions
function showCookieBanner() {
  const consent = getCookieConsent();
  if (!consent) {
    document.getElementById('cookie-consent-banner').style.display = 'block';
  }
}

function getCookieConsent() {
  return JSON.parse(localStorage.getItem('cookie_consent'));
}
// Enhanced cookie consent functions
function saveCookieConsent(analytics = false, preferences = false, marketing = false) {
    const consent = {
        analytics,
        preferences,
        marketing,
        timestamp: new Date().toISOString(),
        version: '1.0'
    };

    try {
        localStorage.setItem('cookie_consent', JSON.stringify(consent));
        document.getElementById('cookie-consent-banner').style.display = 'none';
        document.getElementById('cookie-modal').style.display = 'none';

        // Send consent to server
        sendConsentToServer(analytics, preferences, marketing);

        // Apply preferences immediately
        applyUserPreferences();
    } catch (e) {
        console.error('Error saving cookie consent:', e);
    }
}

function sendConsentToServer(analytics, preferences, marketing) {
    const data = {
        analytics,
        preferences,
        marketing
    };

    fetch("{% url 'cookie_consent' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            console.log('Consent saved successfully');
        } else {
            console.error('Failed to save consent');
        }
    }).catch(error => {
        console.error('Error saving consent:', error);
    });
}

// Helper function to get CSRF token
function getCsrfToken() {
    const csrfCookie = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : '';
}

// Setup event listeners
function setupCookieListeners() {
    // Accept all
    document.getElementById('cookie-accept')?.addEventListener('click', () => {
        saveCookieConsent(true, true, true);
    });

    // Reject all
    document.getElementById('cookie-reject')?.addEventListener('click', () => {
        saveCookieConsent(false, false, false);
    });

    // Open settings
    document.getElementById('cookie-settings')?.addEventListener('click', () => {
        const consent = getCookieConsent() || {};
        document.getElementById('analytics-toggle').checked = consent.analytics || false;
        document.getElementById('preferences-toggle').checked = consent.preferences || false;
        document.getElementById('marketing-toggle').checked = consent.marketing || false;
        document.getElementById('cookie-modal').style.display = 'flex';
    });

    // Save preferences
    document.getElementById('save-preferences')?.addEventListener('click', () => {
        const analytics = document.getElementById('analytics-toggle').checked;
        const preferences = document.getElementById('preferences-toggle').checked;
        const marketing = document.getElementById('marketing-toggle').checked;
        saveCookieConsent(analytics, preferences, marketing);
    });

    // Close modal when clicking outside
    document.getElementById('cookie-modal')?.addEventListener('click', (e) => {
        if (e.target === document.getElementById('cookie-modal')) {
            document.getElementById('cookie-modal').style.display = 'none';
        }
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    setupCookieListeners();
    showCookieBanner();
    applyUserPreferences();
});
// Apply user preferences based on consent
function applyUserPreferences() {
    const consent = getCookieConsent() || {};

    // Example: Disable analytics tracking if not consented
    if (!consent.analytics) {
        // Disable analytics scripts here
    }

    // Apply other preferences as needed
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize cookie consent
    showCookieBanner();
    applyUserPreferences();

    // Add modal close handler
    document.getElementById('cookie-modal-close').addEventListener('click', () => {
        document.getElementById('cookie-modal').style.display = 'none';
    });

    // Update tracking functions to respect consent
    const consent = getCookieConsent() || {};

    // Update trackInteraction to respect consent
    const originalTrackInteraction = trackInteraction;
    window.trackInteraction = function(data) {
        if (data.type === 'analytics_event' && !consent.analytics) return;
        originalTrackInteraction(data);
    };

    // Update trackPageVisit to respect consent
    const originalTrackPageVisit = trackPageVisit;
    window.trackPageVisit = function() {
        if (!consent.analytics) return;
        originalTrackPageVisit();
    };
});
    </script>


     <script>
        // Close mobile menu when clicking a nav link
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', () => {
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    // Bootstrap way to close the collapse
                    bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
                }
            });
        });

    </script>

       <script>
        // Contact Modal Functionality
        const contactModal = document.getElementById('contactModal');
        const offerTitle = document.getElementById('offerTitle');
        const offerDesc = document.getElementById('offerDesc');
        const closeModal = document.getElementById('closeModal');

        // Function to open modal with content
        function openContactModal(title, description) {
            offerTitle.textContent = title;
            offerDesc.textContent = description;
            contactModal.style.display = 'flex';
        }

        // Claim Offer Buttons
        document.querySelectorAll('.claim-offer-btn').forEach(button => {
            button.addEventListener('click', function() {
                const title = this.getAttribute('data-offer-title');
                const desc = this.getAttribute('data-offer-desc');
                openContactModal(title, desc);
            });
        });

    // Download buttons handler - simplified and moved to main DOMContentLoaded
    function setupDownloadButtons() {
        const downloadUrls = {
            'orion': 'http://start.orionstars.vip:8580/index.html',
            'firekirin': 'http://start.firekirin.xyz:8580/index.html',
            'juwa': 'https://dl.juwa777.com',
            'ultrapanda': 'https://www.ultrapanda.mobi/',
            'pandamaster': 'https://pandamaster.com',
            'vegas': 'https://m.lasvegassweeps.com/',
            'gamevault': 'https://download.gamevault999.com/',
            'vblink': 'https://vblink.net/'
        };

        document.querySelectorAll('.btn-download').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();  // Prevent default behavior
                const game = this.getAttribute('data-game');
                if (downloadUrls[game]) {
                    window.open(downloadUrls[game], '_blank');
                } else {
                    alert('Download link not available. Please contact support.');
                }
            });
        });
    }

        // Game Footer Buttons
        document.querySelectorAll('.contact-for-game').forEach(button => {
            button.addEventListener('click', function() {
                const gameName = this.getAttribute('data-game-name');
                const startText = gameName.includes('Orion')
                    ? 'Ready to play Orion Stars? Contact us to get started!'
                    : `Ready to play ${gameName}? Contact us to get started!`;
                openContactModal(`Play ${gameName}`, startText);
            });
        });

        // Hero Play Now Button
        document.querySelector('.hero-section .btn-light').addEventListener('click', function(e) {
            e.preventDefault();
            openContactModal('Get Started', 'Ready to play? Contact us to get started with your account!');
        });

        // Contact Options
        document.querySelectorAll('.contact-option').forEach(option => {
            option.addEventListener('click', function() {
                const contactMethod = this.getAttribute('data-contact');
                let url;

                switch(contactMethod) {
                    case 'whatsapp':
                        url = "{{ social.whatsapp }}";
                        break;
                    case 'facebook':
                        url = "{{ social.facebook }}";
                        break;
                    case 'telegram':
                        url = "{{ social.telegram }}";
                        break;
                }

                if(url) {
                    // Add the offer/game to the message
                    const message = encodeURIComponent(`I want ${offerTitle.textContent}`);
                    window.open(`${url}?text=${message}`, '_blank');
                }

                contactModal.style.display = 'none';
            });
        });

        // Close Modal
        closeModal.addEventListener('click', function() {
            contactModal.style.display = 'none';
        });

        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === contactModal) {
                contactModal.style.display = 'none';
            }
        });

         // Initialize variables
    let lastWinId = {% if live_wins.0.id %}{{ live_wins.0.id }}{% else %}0{% endif %};
    let currentOfferId = {% if active_offer %}{{ active_offer.id }}{% elif future_offer %}{{ future_offer.id }}{% else %}null{% endif %};
    let isPollingActive = true;
    let lastServerUpdate = Date.now();
    let serverCountdownSeconds = {% if active_offer %}{{ active_offer.time_remaining.total_seconds|default:0|floatformat:0 }}{% elif future_offer %}{{ future_offer.time_until_start.total_seconds|default:0|floatformat:0 }}{% else %}0{% endif %};
    let countdownInterval;
    let hiddenStartTime;

    // Function to update countdown display
    function updateCountdownDisplay() {
        // Clear any existing interval
        clearInterval(countdownInterval);

        // Calculate elapsed time since last server sync
        const elapsedSeconds = Math.floor((Date.now() - lastServerUpdate) / 1000);
        let remainingSeconds = Math.max(0, serverCountdownSeconds - elapsedSeconds);

        if (remainingSeconds <= 0) {
            document.getElementById("countdown-timer").innerHTML = "OFFER EXPIRED!";
            setTimeout(() => location.reload(), 5000);
            return;
        }

        // Start a new interval for smooth countdown
        countdownInterval = setInterval(() => {
            remainingSeconds--;

            if (remainingSeconds <= 0) {
                clearInterval(countdownInterval);
                document.getElementById("countdown-timer").innerHTML = "OFFER EXPIRED!";
                setTimeout(() => location.reload(), 5000);
                return;
            }

            const hours = Math.floor(remainingSeconds / 3600);
            const minutes = Math.floor((remainingSeconds % 3600) / 60);
            const secondsRemaining = remainingSeconds % 60;

            const status = "{% if active_offer %}ENDS IN:{% else %}STARTS IN:{% endif %}";
            document.getElementById("countdown-timer").innerHTML =
                `${status} ${hours}h ${minutes}m ${secondsRemaining}s`;
        }, 1000);
    }

    // Polling function to get updates
    function pollUpdates() {
        if (!isPollingActive) return;

        fetch(`/updates/?last_win_id=${lastWinId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                // Update last server sync time
                lastServerUpdate = Date.now();

                // Process new wins
                if (data.wins && data.wins.length > 0) {
                    const marquee = document.querySelector('marquee');
                    data.wins.forEach(win => {
                        if (win.username && win.amount) {
                            marquee.innerHTML += ` 🎉 ${win.username} Won $${win.amount}! `;
                        }                    });

                    // Update lastWinId to the latest win id
                    lastWinId = data.last_win_id;

                    // Limit the number of displayed wins
                    const wins = marquee.innerHTML.split('🎣');
                    if (wins.length > 10) {
                        marquee.innerHTML = wins.slice(-10).join('🎣');
                    }
                }

                // Process offers
                if (data.offers && data.offers.length > 0) {
                    // Check if current offer is still active
                    const currentOfferActive = data.offers.some(o => o.id === currentOfferId);

                    if (!currentOfferActive && currentOfferId) {
                        // Reload if current offer expired
                        document.getElementById("countdown-timer").innerHTML = "OFFER EXPIRED!";
                        setTimeout(() => location.reload(), 5000);
                    } else {
                        // Update countdown timers
                        data.offers.forEach(offer => {
                            if (offer.id === currentOfferId) {
                                serverCountdownSeconds = offer.countdown;
                                updateCountdownDisplay();
                            }
                        });
                    }
                }

                // Schedule next poll
                setTimeout(pollUpdates, 15000);
            })
            .catch(error => {
                console.error('Polling error:', error);
                // Retry after 30 seconds on error
                setTimeout(pollUpdates, 30000);
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize download buttons
        setupDownloadButtons();

        // Start polling when page loads
        pollUpdates();

        // Initialize countdown if offer exists
        if (serverCountdownSeconds > 0) {
            updateCountdownDisplay();
        }

        // Track all button clicks
        document.body.addEventListener('click', function(e) {
            const target = e.target.closest('button, a');
            if (target) {
                let type = 'button_click';
                if (target.tagName === 'A') type = 'link_click';

                // Get the element text
                let text = target.innerText || target.textContent;
                text = text.substring(0, 100); // Limit length

                trackInteraction({
                    type: type,
                    element_id: target.id || '',
                    page_path: window.location.pathname,
                    data: {
                        text: text.trim(),
                        classes: target.className
                    }
                });
            }
        });

        // Special offer interest tracking
        document.querySelectorAll('.offer-card').forEach(card => {
            card.addEventListener('click', () => {
                // Get offer title if available
                const titleElement = card.querySelector('h5, h6');
                const title = titleElement ? titleElement.innerText : 'Unknown Offer';

                trackInteraction({
                    type: 'offer_interest',
                    page_path: window.location.pathname,
                    data: {
                        offer_title: title.substring(0, 100)
                    }
                });
            });
        });

        // Close mobile menu when clicking a nav link
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', () => {
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    // Bootstrap way to close the collapse
                    bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
                }
            });
        });

        function trackInteraction(data) {
            const consent = getCookieConsent();
             // Skip if analytics not consented
            if (data.type === 'analytics_event' && !(consent && consent.analytics)) return;
            if (!{{ tracking_enabled|yesno:"true,false" }}) return;

            // Add CSRF token for security
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            fetch("{% url 'track_interaction' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken || ''
                },
                body: JSON.stringify(data)
            }).catch(error => console.error('Tracking error:', error));
        }

        // Initialize country detection for page visits
        trackPageVisit();
    });

    // Track page visits with country
// Global variable to store detected country
  // In your base template
  // Global variable to store detected country
let detectedCountry = null;
let lastPingTime = Date.now();

function trackPageVisit(useBeacon = false) {
    const consent = getCookieConsent();
    if (!(consent && consent.analytics)) return;
    const now = Date.now();
    const timeSinceLast = (now - lastPingTime) / 1000; // in seconds
    lastPingTime = now;

    // Only send ping if user was active recently
    if (timeSinceLast < 300) {
        sendVisitData(detectedCountry, useBeacon);
    }
}

function sendVisitData(country, useBeacon) {
    const data = { country: country || 'Unknown' };

    if (useBeacon && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
        navigator.sendBeacon("{% url 'track_page_visit' %}", blob);
    } else {
        fetch("{% url 'track_page_visit' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': "{{ csrf_token }}"
            },
            body: JSON.stringify(data)
        }).catch(error => console.error('Tracking error:', error));
    }
}

// Detect country first
function detectCountry() {
    fetch("https://ipapi.co/json/")
        .then(response => response.json())
        .then(data => {
            detectedCountry = data.country_name || 'Unknown';
            // Send initial visit with country
            trackPageVisit();
        })
        .catch(() => {
            detectedCountry = 'Unknown';
            trackPageVisit();
        });
}

// Initialize tracking
document.addEventListener('DOMContentLoaded', () => {
    detectCountry();

    // Set up periodic pings every 30 seconds
    setInterval(() => trackPageVisit(), 30000);
});

// Final ping when user leaves
window.addEventListener('beforeunload', () => trackPageVisit(true));

// Track user activity to reset idle timer
document.addEventListener('mousemove', () => lastPingTime = Date.now());
document.addEventListener('keypress', () => lastPingTime = Date.now());
    // Handle visibility changes
// Track page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') {
            // Send final ping when user leaves
            trackPageVisit();
        }
    });

    // Send periodic updates every 30 seconds
    setInterval(trackPageVisit, 30000);

    function trackPageVisit() {
        fetch("https://ipapi.co/json/")
            .then(response => response.json())
            .then(data => {
                const country = data.country_name || 'Unknown';

                fetch("{% url 'track_page_visit' %}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({
                        country: country
                    })
                });
            })
            .catch(() => {
                // Fallback if IP detection fails
                fetch("{% url 'track_page_visit' %}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({
                        country: 'Unknown'
                    })
                });
            });
    }

    // Initial page visit tracking
    document.addEventListener('DOMContentLoaded', trackPageVisit);
    // Clean up when navigating away
    window.addEventListener('beforeunload', function() {
        isPollingActive = false;
        clearInterval(countdownInterval);
    });
</script>    <style>