document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    if (!body) return;

    const theme = body.dataset.theme || "dark";
    const compact = body.dataset.compact === "true";

    body.classList.remove("theme-dark", "theme-light");
    body.classList.add(`theme-${theme}`);

    if (compact) {
        body.classList.add("compact-mode");
    } else {
        body.classList.remove("compact-mode");
    }
});