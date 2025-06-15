let countdownInterval;
let lastServerUpdate = Date.now();
let serverCountdownSeconds = 0;

function updateCountdownDisplay() {
    clearInterval(countdownInterval);
    const elapsedSeconds = Math.floor((Date.now() - lastServerUpdate) / 1000);
    let remainingSeconds = Math.max(0, serverCountdownSeconds - elapsedSeconds);

    if (remainingSeconds <= 0) {
        document.getElementById("countdown-timer").innerHTML = "OFFER EXPIRED!";
        setTimeout(() => location.reload(), 5000);
        return;
    }

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
