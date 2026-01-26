/* ===== Count Up Animation ===== */
function animateCount(el, start, end, duration = 1500) {
    let startTime = null;

    function update(currentTime) {
        if (!startTime) startTime = currentTime;
        const progress = Math.min((currentTime - startTime) / duration, 1);
        
        // Calculate current number
        const value = Math.floor(progress * (end - start) + start);
        
        // 🟢 JUST THE NUMBER (No prefix needed)
        el.textContent = value.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = end.toLocaleString(); 
        }
    }
    requestAnimationFrame(update);
}

/* ===== Initialize Stats on Load ===== */
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".stat-value").forEach(el => {
        const rawValue = el.getAttribute("data-value") || "0";
        const value = parseFloat(rawValue.replace(/,/g, ''));
        animateCount(el, 0, value);
    });
});

/* ===== Dynamic Update Handler (for future websocket/ajax use) ===== */
function updateStat(el, newValue) {
    const oldValue = parseInt(el.getAttribute("data-value") || 0);
    el.setAttribute("data-value", newValue);

    // animate number
    animateCount(el, oldValue, newValue, 800);

    // pulse effect
    el.classList.remove("pulse");
    void el.offsetWidth; // trigger reflow
    el.classList.add("pulse");

    // glow logic based on value change
    const card = el.closest(".stat-card");
    card.classList.remove("glow-green", "glow-red", "glow-neutral");

    if (newValue > oldValue) {
        card.classList.add("glow-green");
    } else if (newValue < oldValue) {
        card.classList.add("glow-red");
    } else {
        card.classList.add("glow-neutral");
    }

    // remove glow after animation
    setTimeout(() => {
        card.classList.remove("glow-green", "glow-red", "glow-neutral");
    }, 1200);
}