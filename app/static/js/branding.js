// app/static/js/branding.js
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        if (document.title.includes("PDF") || document.title.includes("Tools")) {
            document.title = `${config.appName} - ${config.tagline}`;
        }

        document.querySelectorAll('.brand-title, .logo-text, .navbar-brand').forEach(el => {
            el.innerHTML = `${config.logoEmoji} ${config.appName}`;
        });

        document.querySelectorAll('.footer-text, footer p').forEach(el => {
            if (el.textContent.includes("reserved") || el.textContent.includes("©")) {
                el.textContent = config.footer;
            }
        });
    } catch (error) {
        console.error("Failed to load branding config:", error);
    }
});
