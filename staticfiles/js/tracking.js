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
// Enhanced Tracking & Analytics
// ======================
let detectedCountry = null;
let lastPingTime = Date.now();
let sessionStartTime = Date.now();

// Enhanced cookie management
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
}

// Session management
function getSessionKey() {
    let sessionKey = localStorage.getItem('session_key');
    if (!sessionKey) {
        sessionKey = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('session_key', sessionKey);
    }
    return sessionKey;
}

// Enhanced consent checking
function getCookieConsent() {
    try {
        const consent = localStorage.getItem('cookie_consent');
        return consent ? JSON.parse(consent) : null;
    } catch (e) {
        console.error('Error parsing cookie consent:', e);
        return null;
    }
}

// Enhanced interaction tracking
function trackInteraction(type, element, additionalData = {}) {
    const consent = getCookieConsent();
    if (!consent || !consent.analytics) return;

    try {
        const csrfToken = getCookie('csrftoken') || '';
        if (!csrfToken) {
            console.warn('CSRF token missing for interaction tracking');
            return;
        }

        // Enhanced element data collection
        const elementData = {
            id: element?.id || '',
            tag: element?.tagName || '',
            classes: element?.className || '',
            text: (element?.textContent || '').substring(0, 200).trim(),
            href: element?.href || '',
            position: element ? getElementPosition(element) : null
        };

        const interactionData = {
            type,
            session_key: getSessionKey(),
            page_path: window.location.pathname,
            timestamp: new Date().toISOString(),
            element: elementData,
            additional_data: additionalData,
            session_duration: (Date.now() - sessionStartTime) / 1000,
            scroll_position: window.scrollY,
            viewport_size: `${window.innerWidth}x${window.innerHeight}`
        };

        fetch(window.CONFIG.urls.trackInteraction, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(interactionData)
        }).catch(error => console.error('Interaction tracking error:', error));

    } catch (error) {
        console.error('Error in trackInteraction:', error);
    }
}

// Helper to get element position
function getElementPosition(element) {
    const rect = element.getBoundingClientRect();
    return {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height,
        visibility: (rect.top >= 0 && rect.bottom <= window.innerHeight) ? 'fully' :
                   (rect.bottom < 0 || rect.top > window.innerHeight) ? 'hidden' : 'partial'
    };
}

// Enhanced visit tracking
function sendVisitData(country, useBeacon = false) {
    const consent = getCookieConsent();
    if (!consent || !consent.analytics) return;

    const data = {
        country: country || 'Unknown',
        path: window.location.pathname,
        referrer: document.referrer || '',
        session_key: getSessionKey(),
        page_title: document.title,
        user_agent: navigator.userAgent,
        screen_resolution: `${screen.width}x${screen.height}`,
        time_on_page: (Date.now() - lastPingTime) / 1000
    };

    if (useBeacon && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
        navigator.sendBeacon(window.CONFIG.urls.trackPageVisit, blob);
    } else {
        fetch(window.CONFIG.urls.trackPageVisit, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || ''
            },
            body: JSON.stringify(data)
        }).catch(error => console.error('Visit tracking error:', error));
    }
}

// Enhanced analytics event tracking
function trackAnalyticsEvent(category, action, label, value = 0) {
    const consent = getCookieConsent();
    if (!consent || !consent.analytics) return;

    const csrfToken = getCookie('csrftoken') || '';
    if (!csrfToken) {
        console.warn('CSRF token missing for analytics tracking');
        return;
    }

    const eventData = {
        category,
        action,
        label,
        value,
        path: window.location.pathname,
        session_key: getSessionKey(),
        timestamp: new Date().toISOString()
    };

    fetch(window.CONFIG.urls.trackEvent, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(eventData)
    }).catch(error => console.error('Analytics tracking error:', error));
}

// Enhanced country detection
function detectCountry() {
    fetch("https://ipapi.co/json/")
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            detectedCountry = data.country_name || 'Unknown';
            setCookie('user_country', detectedCountry, 7); // Store for 7 days
            trackPageVisit();
            trackAnalyticsEvent('System', 'Country Detected', detectedCountry);
        })
        .catch(error => {
            console.error('Country detection error:', error);
            detectedCountry = getCookie('user_country') || 'Unknown';
            trackPageVisit();
        });
}

// Enhanced setupTracking with more event types
function setupTracking() {
    // Button and link tracking
    document.body.addEventListener('click', function(e) {
        const target = e.target.closest('button, a, [data-track]');
        if (target) {
            const type = target.tagName === 'A' ? 'link_click' :
                        target.tagName === 'BUTTON' ? 'button_click' :
                        'custom_click';

            const customData = target.dataset.track ?
                JSON.parse(target.dataset.track) : {};

            trackInteraction(type, target, {
                ...customData,
                text: (target.innerText || target.textContent).substring(0, 200).trim(),
                href: target.href || ''
            });
        }
    });

    // Form interactions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            trackInteraction('form_submit', form, {
                form_id: form.id || '',
                form_class: form.className || '',
                inputs_count: form.elements.length
            });
        });
    });

    // Enhanced offer tracking
    document.querySelectorAll('.offer-card, .claim-offer-btn').forEach(element => {
        element.addEventListener('click', function() {
            const title = this.getAttribute('data-offer-title') ||
                         this.closest('.offer-card')?.querySelector('h5, h6')?.innerText ||
                         'Unknown Offer';

            trackInteraction('offer_interest', this, {
                offer_id: this.getAttribute('data-offer-id') || '',
                offer_title: title.substring(0, 200),
                offer_type: this.getAttribute('data-offer-type') || '',
                position_in_list: getElementIndex(this)
            });
        });
    });

    // Enhanced game interest tracking
    document.querySelectorAll('.contact-for-game').forEach(button => {
        button.addEventListener('click', function() {
            const gameName = this.getAttribute('data-game-name') || 'Unknown Game';
            trackInteraction('game_interest', this, {
                game_name: gameName,
                game_id: this.getAttribute('data-game-id') || '',
                source: this.getAttribute('data-source') || 'button'
            });
        });
    });

    // Scroll depth tracking
    let scrollDepthTracked = [];
    window.addEventListener('scroll', function() {
        const depth = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
        if (depth > 0 && !scrollDepthTracked.includes(depth) {
            if (depth % 25 === 0 || depth > Math.max(...scrollDepthTracked, 0)) {
                trackAnalyticsEvent('Engagement', 'Scroll Depth', `${depth}%`);
                scrollDepthTracked.push(depth);
            }
        }
    });

    // Time-based tracking
    detectCountry();
    setInterval(() => trackPageVisit(), 30000);
    trackAnalyticsEvent('Page', 'view', document.title);

    // Session tracking
    window.addEventListener('beforeunload', function() {
        trackAnalyticsEvent('Session', 'end', 'Page unload',
            (Date.now() - sessionStartTime) / 1000);
    });
}

// Helper to get element index in parent
function getElementIndex(element) {
    if (!element.parentNode) return -1;
    return Array.from(element.parentNode.children).indexOf(element);
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
    // localStorage.setItem('flashClosed', Date.now());
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

    function shuffleArray(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    }

  function showAd() {
    // Clear any pending ad timeout
    clearTimeout(adTimeout);

     // Shuffle the ad types each cycle
  const shuffledTypes = shuffleArray([...adTypes]);
  const adType = shuffledTypes[0];

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
    // if (lastClose && (Date.now() - lastClose < 86400000)) return;

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
    // if (lastClose && (Date.now() - lastClose < 86400000)) return;

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
    // if (lastClose && (Date.now() - lastClose < 86400000)) return;

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