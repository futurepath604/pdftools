// app/static/js/ads-manager.js
(function() {
    // --- PAGE-WISE & POSITION-WISE AD CODES ---
    const AD_DATABASE = {
        "default": {
            "header-ad": `<div style="text-align:center; padding:10px; background:#fafafa; border:1px dashed #ddd;"><small>Default Header Ad</small></div>`,
            "footer-ad": `<div style="text-align:center; padding:10px; background:#fafafa; border:1px dashed #ddd;"><small>Default Footer Ad</small></div>`
        },
        "index.html": {
            "header-ad": `<div style="text-align:center; padding:10px;"><small>Home Top Banner Ad</small></div>`,
            "hero-ad": `<div style="text-align:center; padding:10px;"><small>Home Hero Section Ad</small></div>`,
            "footer-ad": `<div style="text-align:center; padding:10px;"><small>Home Footer Ad</small></div>`
        },
        "compress.html": {
            "header-ad": `<div style="text-align:center; padding:10px;"><small>Compress Top Ad</small></div>`,
            "tool-box-ad": `<div style="text-align:center; padding:10px; background:#fff3cd;"><small>Compress Buttoner Niche Special Ad</small></div>`,
            "footer-ad": `<div style="text-align:center; padding:10px;"><small>Compress Footer Ad</small></div>`
        },
        "merge.html": {
            "header-ad": `<div style="text-align:center; padding:10px;"><small>Merge Top Ad</small></div>`,
            "tool-box-ad": `<div style="text-align:center; padding:10px; background:#d4edda;"><small>Merge Tool Box Ad</small></div>`,
            "footer-ad": `<div style="text-align:center; padding:10px;"><small>Merge Footer Ad</small></div>`
        }
    };

    document.addEventListener("DOMContentLoaded", () => {
        let path = window.location.pathname.split("/").pop();
        if (path === "" || path === "/") path = "index.html";

        const pageAds = AD_DATABASE[path] || AD_DATABASE["default"];
        const globalAds = AD_DATABASE["default"];

        document.querySelectorAll("[id^='ad-slot-'], [id$='-ad']").forEach(el => {
            const slotId = el.id;
            const adHtml = (pageAds && pageAds[slotId]) ? pageAds[slotId] : (globalAds[slotId] || "");
            if (adHtml) {
                el.innerHTML = adHtml;
            }
        });
    });
})();
