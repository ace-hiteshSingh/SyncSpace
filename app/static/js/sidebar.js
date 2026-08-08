document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggleButton = document.getElementById("sidebarToggle");
    const closeButton = document.getElementById("sidebarClose");


    // -----------------------------------------
    // OPEN SIDEBAR
    // -----------------------------------------

    function openSidebar() {

        if (!sidebar) return;

        sidebar.classList.add("open");

        if (overlay) {
            overlay.classList.add("active");
            overlay.setAttribute("aria-hidden", "false");
        }

        if (toggleButton) {
            toggleButton.setAttribute("aria-expanded", "true");
        }

        document.body.classList.add("sidebar-open");
    }


    // -----------------------------------------
    // CLOSE SIDEBAR
    // -----------------------------------------

    function closeSidebar() {

        if (!sidebar) return;

        sidebar.classList.remove("open");

        if (overlay) {
            overlay.classList.remove("active");
            overlay.setAttribute("aria-hidden", "true");
        }

        if (toggleButton) {
            toggleButton.setAttribute("aria-expanded", "false");
        }

        document.body.classList.remove("sidebar-open");
    }


    // -----------------------------------------
    // TOGGLE SIDEBAR
    // -----------------------------------------

    if (toggleButton) {

        toggleButton.addEventListener("click", () => {

            if (sidebar?.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }

        });

    }


    // -----------------------------------------
    // CLOSE BUTTON
    // -----------------------------------------

    if (closeButton) {
        closeButton.addEventListener("click", closeSidebar);
    }


    // -----------------------------------------
    // CLICK OUTSIDE SIDEBAR
    // -----------------------------------------

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }


    // -----------------------------------------
    // CLOSE AFTER CLICKING A LINK
    // -----------------------------------------

    if (sidebar) {

        const sidebarLinks = sidebar.querySelectorAll("a");

        sidebarLinks.forEach((link) => {

            link.addEventListener("click", () => {

                if (window.innerWidth <= 768) {
                    closeSidebar();
                }

            });

        });

    }


    // -----------------------------------------
    // CLOSE ON ESC
    // -----------------------------------------

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeSidebar();
        }

    });


    // -----------------------------------------
    // RESET ON DESKTOP
    // -----------------------------------------

    window.addEventListener("resize", () => {

        if (window.innerWidth > 768) {
            closeSidebar();
        }

    });

});