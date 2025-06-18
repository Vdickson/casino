const contactModal = document.getElementById('contactModal');
const offerTitle = document.getElementById('offerTitle');
const offerDesc = document.getElementById('offerDesc');
const closeModal = document.getElementById('closeModal');

function openContactModal(title, description) {
    offerTitle.textContent = title;
    offerDesc.textContent = description;
    contactModal.style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.claim-offer-btn').forEach(button => {
        button.addEventListener('click', function () {
            openContactModal(this.dataset.offerTitle, this.dataset.offerDesc);
        });
    });

    document.querySelectorAll('.contact-for-game').forEach(button => {
        button.addEventListener('click', function () {
            openContactModal(`Play ${this.dataset.gameName}`, `Ready to play ${this.dataset.gameName}? Contact us to get started!`);
        });
    });

    document.querySelector('.hero-section .btn-light')?.addEventListener('click', e => {
        e.preventDefault();
        openContactModal('Get Started', 'Ready to play? Contact us to get started with your account!');
    });

    document.querySelectorAll('.contact-option').forEach(option => {
        option.addEventListener('click', function () {
            const contactMethod = this.dataset.contact;
            let url;
            switch (contactMethod) {
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
            if (url) {
                const message = encodeURIComponent(`I want ${offerTitle.textContent}`);
                window.open(`${url}?text=${message}`, '_blank');
            }
            contactModal.style.display = 'none';
        });
    });

    closeModal?.addEventListener('click', () => contactModal.style.display = 'none');

    window.addEventListener('click', event => {
        if (event.target === contactModal) {
            contactModal.style.display = 'none';
        }
    });
});
