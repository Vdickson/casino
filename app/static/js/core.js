// core.js
// Add this at the top of core.js
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
// Add this function to track analytics events
function trackAnalyticsEvent(category, action, label, value = 0) {
    const consent = getCookieConsent();
    if (!consent || !consent.analytics) return;

    const data = {
        category: category,
        action: action,
        label: label,
        value: value,  // Use 'value' not 'event_value'
        path: window.location.pathname
    };

    fetch(window.CONFIG.urls.trackEvent, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify(data)
    }).catch(error => console.error('Analytics tracking error:', error));
}function trackAnalyticsEvent(category, action, label, value = 0) {
    const consent = getCookieConsent();
    if (!consent || !consent.analytics) return;

    const data = {
        category: category,
        action: action,
        label: label,
        value: value,
        path: window.location.pathname
    };

    fetch(window.CONFIG.urls.trackEvent, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify(data)
    }).catch(error => console.error('Analytics tracking error:', error));
}

// ======================
// Contact Modal Functionality
// ======================
const contactModal = document.getElementById('contactModal');
const offerTitle = document.getElementById('offerTitle');
const offerDesc = document.getElementById('offerDesc');
const closeModal = document.getElementById('closeModal');

function openContactModal(title, description) {
    if (offerTitle && offerDesc && contactModal) {
        offerTitle.textContent = title;
        offerDesc.textContent = description;
        contactModal.style.display = 'flex';
    }
}

function setupContactModalListeners() {
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
            const startText = gameName.includes('Orion') ?
                'Ready to play Orion Stars? Contact us to get started!' :
                `Ready to play ${gameName}? Contact us to get started!`;
            openContactModal(`Play ${gameName}`, startText);
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

    // Contact Options
    document.querySelectorAll('.contact-option').forEach(option => {
        option.addEventListener('click', function() {
            const contactMethod = this.getAttribute('data-contact');
            const social = window.CONFIG.social;
            let url = social[contactMethod];

            if (url && offerTitle) {
                const message = encodeURIComponent(`I want ${offerTitle.textContent}`);
                window.open(`${url}?text=${message}`, '_blank');
            }

            if (contactModal) {
                contactModal.style.display = 'none';
            }
        });
    });

    // Close Modal
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            if (contactModal) {
                contactModal.style.display = 'none';
            }
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === contactModal) {
            contactModal.style.display = 'none';
        }
    });
}

// ======================
// Game Download Functionality
// ======================
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
            e.preventDefault();
            const game = this.getAttribute('data-game');
            if (downloadUrls[game]) {
                window.open(downloadUrls[game], '_blank');
            } else {
                alert('Download link not available. Please contact support.');
            }
        });
    });
}

// ======================
// Countdown Timer & Polling
// ======================
let lastWinId = window.CONFIG.lastWinId;
let currentOfferId = window.CONFIG.currentOfferId;
let isPollingActive = true;
let lastServerUpdate = Date.now();
let serverCountdownSeconds = window.CONFIG.serverCountdownSeconds;
let countdownInterval;

function updateCountdownDisplay() {
    clearInterval(countdownInterval);

    const elapsedSeconds = Math.floor((Date.now() - lastServerUpdate) / 1000);
    let remainingSeconds = Math.max(0, serverCountdownSeconds - elapsedSeconds);

    const countdownTimer = document.getElementById("countdown-timer");
    if (!countdownTimer) return;

    if (remainingSeconds <= 0) {
        countdownTimer.innerHTML = "OFFER EXPIRED!";
        setTimeout(() => location.reload(), 5000);
        return;
    }

    countdownInterval = setInterval(() => {
        remainingSeconds--;

        if (remainingSeconds <= 0) {
            clearInterval(countdownInterval);
            countdownTimer.innerHTML = "OFFER EXPIRED!";
            setTimeout(() => location.reload(), 5000);
            return;
        }

        const hours = Math.floor(remainingSeconds / 3600);
        const minutes = Math.floor((remainingSeconds % 3600) / 60);
        const secondsRemaining = remainingSeconds % 60;

        const status = window.CONFIG.countdownStatus;
        countdownTimer.innerHTML = `${status} ${hours}h ${minutes}m ${secondsRemaining}s`;
    }, 1000);
}

function pollUpdates() {
    if (!isPollingActive) return;

    fetch(`/updates/?last_win_id=${lastWinId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            lastServerUpdate = Date.now();

            // Process new wins
            if (data.wins && data.wins.length > 0) {
                const marquee = document.querySelector('marquee');
                if (marquee) {
                    data.wins.forEach(win => {
                        if (win.username && win.amount) {
                            marquee.innerHTML += ` 🎉 ${win.username} Won $${win.amount}! `;
                        }
                    });
                    lastWinId = data.last_win_id;

                    // Limit displayed wins
                    const wins = marquee.innerHTML.split('🎣');
                    if (wins.length > 10) {
                        marquee.innerHTML = wins.slice(-10).join('🎣');
                    }
                }
            }

            // Process offers
            if (data.offers && data.offers.length > 0) {
                const currentOfferActive = data.offers.some(o => o.id === currentOfferId);

                if (!currentOfferActive && currentOfferId) {
                    const countdownTimer = document.getElementById("countdown-timer");
                    if (countdownTimer) {
                        countdownTimer.innerHTML = "OFFER EXPIRED!";
                    }
                    setTimeout(() => location.reload(), 5000);
                } else {
                    data.offers.forEach(offer => {
                        if (offer.id === currentOfferId) {
                            serverCountdownSeconds = offer.countdown;
                            updateCountdownDisplay();
                        }
                    });
                }
            }

            setTimeout(pollUpdates, 15000);
        })
        .catch(error => {
            console.error('Polling error:', error);
            setTimeout(pollUpdates, 30000);
        });
}

// ======================
// Navigation & Mobile Menu
// ======================
function setupNavigation() {
    // Close mobile menu when clicking a nav link
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
            }
        });
    });
}

// ======================
// Tracking & Analytics
// ======================
let detectedCountry = null;
let lastPingTime = Date.now();

function trackInteraction(data) {
    // const consent = getCookieConsent();
    // Get consent from localStorage instead of function
    const consent = JSON.parse(localStorage.getItem('cookie_consent') || {});
    if (data.type === 'analytics_event' && !(consent && consent.analytics)) return;
    if (!window.CONFIG.trackingEnabled) return;

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    fetch(window.CONFIG.urls.trackInteraction, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    }).catch(error => console.error('Tracking error:', error));
}

function sendVisitData(country, useBeacon = false) {
    const data = { country: country || 'Unknown' };

    if (useBeacon && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
        navigator.sendBeacon(window.CONFIG.urls.trackPageVisit, blob);
    } else {
        fetch(window.CONFIG.urls.trackPageVisit, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CONFIG.csrfToken
            },
            body: JSON.stringify(data)
        }).catch(error => console.error('Tracking error:', error));
    }
}

function trackPageVisit(useBeacon = false) {
    const consent = getCookieConsent();
    if (!(consent && consent.analytics)) return;

    const now = Date.now();
    const timeSinceLast = (now - lastPingTime) / 1000;
    lastPingTime = now;

    if (timeSinceLast < 300) {
        sendVisitData(detectedCountry, useBeacon);
        // Track as analytics event too
        trackAnalyticsEvent('Engagement', 'visit', detectedCountry, parseInt(timeSinceLast));
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

function setupTracking() {
    // Button and link tracking
    document.body.addEventListener('click', function(e) {
        const target = e.target.closest('button, a');
        if (target) {
            const type = target.tagName === 'A' ? 'link_click' : 'button_click';
            const text = (target.innerText || target.textContent).substring(0, 100).trim();

            trackInteraction({
                type: type,
                element_id: target.id || '',
                page_path: window.location.pathname,
                data: { text, classes: target.className }
            });
        }
    });

    // Offer interest tracking
    document.querySelectorAll('.offer-card').forEach(card => {
        card.addEventListener('click', () => {
            const titleElement = card.querySelector('h5, h6');
            const title = titleElement ? titleElement.innerText : 'Unknown Offer';
            trackInteraction({
                type: 'offer_interest',
                page_path: window.location.pathname,
                data: { offer_title: title.substring(0, 100) }
            });
        });
    });

    // Country detection and periodic tracking
    detectCountry();
    setInterval(() => trackPageVisit(), 30000);
}

// ======================
// Cookie Consent
// ======================
function showCookieBanner() {
    const consent = getCookieConsent();
    if (!consent) {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) banner.style.display = 'block';
    }
}

function getCookieConsent() {
    const consent = localStorage.getItem('cookie_consent');
    return consent ? JSON.parse(consent) : null;
}
function saveCookieConsent(analytics = false, preferences = false, marketing = false) {
    const consent = {
        analytics,
        preferences,
        marketing,
        timestamp: new Date().toISOString(),
        version: '1.0'
    };

    localStorage.setItem('cookie_consent', JSON.stringify(consent));

    // Send to backend
    fetch('/cookie-consent/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ analytics, preferences, marketing })
    }).catch(error => console.error('Error saving consent:', error));

    // UI handling remains the same
    const banner = document.getElementById('cookie-consent-banner');
    const modal = document.getElementById('cookie-modal');
    if (banner) banner.style.display = 'none';
    if (modal) modal.style.display = 'none';
}
function setupCookieConsent() {
    // Accept all
    const cookieAccept = document.getElementById('cookie-accept');
    if (cookieAccept) {
        cookieAccept.addEventListener('click', () => saveCookieConsent(true, true, true));
    }

    // Reject all
    const cookieReject = document.getElementById('cookie-reject');
    if (cookieReject) {
        cookieReject.addEventListener('click', () => saveCookieConsent(false, false, false));
    }

    // Open settings
    const cookieSettings = document.getElementById('cookie-settings');
    if (cookieSettings) {
        cookieSettings.addEventListener('click', () => {
            const consent = getCookieConsent() || {};
            const analyticsToggle = document.getElementById('analytics-toggle');
            const preferencesToggle = document.getElementById('preferences-toggle');
            const marketingToggle = document.getElementById('marketing-toggle');
            const modal = document.getElementById('cookie-modal');
            
            if (analyticsToggle) analyticsToggle.checked = consent.analytics || false;
            if (preferencesToggle) preferencesToggle.checked = consent.preferences || false;
            if (marketingToggle) marketingToggle.checked = consent.marketing || false;
            if (modal) modal.style.display = 'flex';
        });
    }

    // Save preferences
    const savePreferences = document.getElementById('save-preferences');
    if (savePreferences) {
        savePreferences.addEventListener('click', () => {
            const analytics = document.getElementById('analytics-toggle')?.checked || false;
            const preferences = document.getElementById('preferences-toggle')?.checked || false;
            const marketing = document.getElementById('marketing-toggle')?.checked || false;
            saveCookieConsent(analytics, preferences, marketing);
        });
    }

    // Close modal
    const cookieModalClose = document.getElementById('cookie-modal-close');
    if (cookieModalClose) {
        cookieModalClose.addEventListener('click', () => {
            const modal = document.getElementById('cookie-modal');
            if (modal) modal.style.display = 'none';
        });
    }

    // Close modal when clicking outside
    const modal = document.getElementById('cookie-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

// ======================
// Flash Offer Functionality (UPDATED)
// ======================
function setupFlashModal() {
  const flashModal = document.getElementById('flashModal');
  if (!flashModal) return;

  // Close button handler
  document.getElementById('closeFlashModal')?.addEventListener('click', function() {
    flashModal.style.opacity = '0';
    setTimeout(() => {
      flashModal.style.display = 'none';
    }, 300);
    localStorage.setItem('flashClosed', Date.now());
    trackAnalyticsEvent('Offer', 'dismiss', 'Flash Offer');
  });

  // Claim button handler
  document.getElementById('flashClaimBtn')?.addEventListener('click', function() {
    const modal = document.getElementById('flashModal');
    const title = modal.getAttribute('data-offer-title') || 'Special Offer';
    const desc = modal.getAttribute('data-offer-desc') || 'Claim this limited time offer!';

    // Close flash modal
    flashModal.style.opacity = '0';
    setTimeout(() => {
      flashModal.style.display = 'none';
    }, 300);

    // Open contact modal
    openContactModal(title, desc);
  });

  // Close when clicking outside
  flashModal.addEventListener('click', function(e) {
    if (e.target === flashModal) {
      flashModal.style.opacity = '0';
      setTimeout(() => {
        flashModal.style.display = 'none';
      }, 300);
      localStorage.setItem('flashClosed', Date.now());
    }
  });
}

// ======================
// Recommendation Offers Functionality (UPDATED)
// ======================
function setupRecommendationModal() {
  const recommendationModal = document.getElementById('recommendationModal');

  // Close button handler
  document.getElementById('closeRecModal')?.addEventListener('click', function() {
    recommendationModal.style.opacity = '0';
    setTimeout(() => {
      recommendationModal.style.display = 'none';
    }, 500);
    localStorage.setItem('recClosed', Date.now());
  });

  // Claim button handler
  document.getElementById('recClaimBtn')?.addEventListener('click', function() {
    const modal = document.getElementById('recommendationModal');
    const title = modal.getAttribute('data-offer-title') || 'Recommended Offer';
    const desc = modal.getAttribute('data-offer-desc') || 'Claim this special offer!';

    // Close recommendation modal
    recommendationModal.style.opacity = '0';
    setTimeout(() => {
      recommendationModal.style.display = 'none';
    }, 300);

    // Open contact modal
    openContactModal(title, desc);
  });

  // Close when clicking outside
  recommendationModal.addEventListener('click', function(e) {
    if (e.target === recommendationModal) {
      recommendationModal.style.opacity = '0';
      setTimeout(() => {
        recommendationModal.style.display = 'none';
      }, 500);
      localStorage.setItem('recClosed', Date.now());
    }
  });
}

// ======================
// Ad Display Manager (NEW)
// ======================
function initAds() {
  setupFlashModal();
  setupRecommendationModal();

  let adTypes = ['flash', 'recommendation', 'limited'];
  let currentAdIndex = 0;
  let adTimeout;

  function showAd() {
    // Clear any pending ad timeout
    clearTimeout(adTimeout);

    // Check which ad to show next
    const adType = adTypes[currentAdIndex];

    if (adType === 'flash') {
      showFlashOffer();
    } else if (adType === 'recommendation') {
      showRecommendation();
    } else if (adType === 'limited') {
      showLimitedOffer();
    }

    // Rotate to next ad type
    currentAdIndex = (currentAdIndex + 1) % adTypes.length;

    // Schedule next ad
    adTimeout = setTimeout(showAd, 180000); // 3 minutes
  }
  function showFlashOffer() {
    const lastClose = localStorage.getItem('flashClosed');
    if (lastClose && (Date.now() - lastClose < 86400000)) return;

    const flashModal = document.getElementById('flashModal');
    if (!flashModal) return;

    // Set offer data
    const flashOffer = window.CONFIG.flashOffer || {
      title: "Limited Time Offer!",
      description: "Double your first deposit - up to 100% bonus!"
    };

    flashModal.setAttribute('data-offer-title', flashOffer.title);
    flashModal.setAttribute('data-offer-desc', flashOffer.description);
    document.getElementById('flashTitle').textContent = flashOffer.title;
    document.getElementById('flashDesc').textContent = flashOffer.description;

    // Show modal
    flashModal.style.display = 'flex';
    setTimeout(() => {
      flashModal.style.opacity = '1';
    }, 50);

    trackAnalyticsEvent('Offer', 'impression', 'Flash Offer Shown');

    // Auto-hide after 30 seconds
    setTimeout(() => {
      if (flashModal.style.opacity === '1') {
        flashModal.style.opacity = '0';
        setTimeout(() => {
          flashModal.style.display = 'none';
        }, 300);
      }
    }, 30000);
  }

  function showRecommendation() {
    const lastClose = localStorage.getItem('recClosed');
    if (lastClose && (Date.now() - lastClose < 86400000)) return;

    const recommendationModal = document.getElementById('recommendationModal');
    if (!recommendationModal) return;

    // Get random recommendation
    const recommendations = window.CONFIG.recommendedOffers || [
      {title: "Double Your First Deposit!", description: "Get 100% bonus on your first deposit"},
      {title: "Special", description: "30% bonus on all weekend deposits"},
      {title: "Get 15% Cashback", description: "Get 15% cashback bonus when you loose 3 games in rot"},
      {title: "Get 50% Refferral", description: "Get 50% bonus when you refer your friends"}

    ];

    const randomOffer = recommendations[Math.floor(Math.random() * recommendations.length)];

    // Set offer data
    recommendationModal.setAttribute('data-offer-title', randomOffer.title);
    recommendationModal.setAttribute('data-offer-desc', randomOffer.description);
    document.getElementById('recTitle').textContent = randomOffer.title;
    document.getElementById('recDesc').textContent = randomOffer.description;

    // Show modal
    recommendationModal.style.display = 'flex';
    setTimeout(() => {
      recommendationModal.style.opacity = '1';
    }, 50);

    trackAnalyticsEvent('Offer', 'impression', 'Recommendation Shown');

    // Auto-hide after 30 seconds
    setTimeout(() => {
      if (recommendationModal.style.opacity === '1') {
        recommendationModal.style.opacity = '0';
        setTimeout(() => {
          recommendationModal.style.display = 'none';
        }, 500);
      }
    }, 30000);
  }
   // NEW: Show limited offer ad
  function showLimitedOffer() {
    const lastClose = localStorage.getItem('limitedClosed');
    if (lastClose && (Date.now() - lastClose < 86400000)) return;

    const flashModal = document.getElementById('flashModal');
    if (!flashModal) return;

    // Use the active offer from backend
    const limitedOffer = window.CONFIG.flashOffer || {
      title: "Limited Time Offer!",
      description: "Special promotion available now!"
    };

    // Set offer data
    flashModal.setAttribute('data-offer-title', limitedOffer.title);
    flashModal.setAttribute('data-offer-desc', limitedOffer.description);
    document.getElementById('flashTitle').textContent = limitedOffer.title;
    document.getElementById('flashDesc').textContent = limitedOffer.description;

    // Show modal
    flashModal.style.display = 'flex';
    setTimeout(() => {
      flashModal.style.opacity = '1';
    }, 50);

    trackAnalyticsEvent('Offer', 'impression', 'Limited Offer Shown');

    // Auto-hide after 30 seconds
    setTimeout(() => {
      if (flashModal.style.opacity === '1') {
        flashModal.style.opacity = '0';
        setTimeout(() => {
          flashModal.style.display = 'none';
        }, 300);
      }
    }, 30000);
  }

  // NEW: Add close handler for limited offer
  function setupLimitedModal() {
    const flashModal = document.getElementById('flashModal');
    if (!flashModal) return;

    document.getElementById('closeFlashModal')?.addEventListener('click', function() {
      flashModal.style.opacity = '0';
      setTimeout(() => {
        flashModal.style.display = 'none';
      }, 300);
      localStorage.setItem('limitedClosed', Date.now());
      trackAnalyticsEvent('Offer', 'dismiss', 'Limited Offer');
    });

    flashModal.addEventListener('click', function(e) {
      if (e.target === flashModal) {
        flashModal.style.opacity = '0';
        setTimeout(() => {
          flashModal.style.display = 'none';
        }, 300);
        localStorage.setItem('limitedClosed', Date.now());
      }
    });
  }
  // Initialize all modal handlers
  setupFlashModal();
  setupRecommendationModal();
  setupLimitedModal();

  // Show first ad after 10 seconds
  setTimeout(showAd, 10000);
}

// ======================
// Main Initialization
// ======================
document.addEventListener('DOMContentLoaded', function() {
    // Setup core functionality
    setupContactModalListeners();
    setupDownloadButtons();
    setupNavigation();
    setupCookieConsent();
    setupTracking();
// NEW: Initialize flash offers
     // Initialize ads functionality
    // Initialize ads functionality
    initAds();
    // Show cookie banner
    showCookieBanner();

    // Start polling and countdown
    if (serverCountdownSeconds > 0) {
        updateCountdownDisplay();
    }
    pollUpdates();
     // Track initial page view if consent exists
    const consent = getCookieConsent();
    if (consent && consent.analytics) {
        trackAnalyticsEvent('Page', 'view', document.title, 0);
    }
});

 // Track initial page view if consent exists
    const consent = getCookieConsent();
    if (consent && consent.analytics) {
        trackAnalyticsEvent('Page', 'view', document.title, 0);
    }
// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    isPollingActive = false;
    clearInterval(countdownInterval);
    trackPageVisit(true);
});

// Activity tracking
document.addEventListener('mousemove', () => lastPingTime = Date.now());
document.addEventListener('keypress', () => lastPingTime = Date.now());
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden') {
        trackPageVisit(true);
    }
});