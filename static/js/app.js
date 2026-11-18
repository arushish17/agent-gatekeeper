/**
 * app.js - Client-Side Interactivity for Agent Gatekeeper
 * Handles live clock updates, mobile drawer toggle, modal handlers, and UX helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Clock Initialization
    initLiveClock();

    // 2. Mobile Menu Toggle
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // 3. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 6000);
    });
});

/**
 * Updates the header clock with current system time every second.
 */
function initLiveClock() {
    const clockEl = document.querySelector('#liveClock .clock-time');
    if (!clockEl) return;

    function updateTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        clockEl.textContent = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }

    updateTime();
    setInterval(updateTime, 1000);
}
