document.addEventListener("DOMContentLoaded", () => {
    const topBtn = document.getElementById("topBtn");
    const menuBtn = document.getElementById("menuBtn");
    const menuContent = document.getElementById("menuContent");
    const userBtn = document.getElementById("userBtn");
    const userDropdown = document.getElementById("userDropdown");

    if (topBtn) {
        window.addEventListener("scroll", () => {
            topBtn.style.display = window.scrollY > 240 ? "inline-grid" : "none";
        });

        topBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    if (menuBtn && menuContent) {
        menuBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            menuContent.style.display = menuContent.style.display === "block" ? "none" : "block";
        });
    }

    if (userBtn && userDropdown) {
        userBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            userDropdown.classList.toggle("show");
        });
    }

    window.addEventListener("click", () => {
        if (menuContent) {
            menuContent.style.display = "none";
        }

        if (userDropdown) {
            userDropdown.classList.remove("show");
        }
    });

    document.querySelectorAll(".stat-card h2").forEach((stat, index) => {
        stat.animate(
            [
                { opacity: 0, transform: "translateY(8px)" },
                { opacity: 1, transform: "translateY(0)" }
            ],
            {
                duration: 420,
                delay: index * 45,
                easing: "ease-out",
                fill: "both"
            }
        );
    });

    if (window.Chart) {
        const chartDefaults = window.Chart.defaults;
        chartDefaults.color = "#94A3B8";
        chartDefaults.font.family = "Inter, system-ui, sans-serif";
        chartDefaults.plugins.legend.labels.boxWidth = 10;
    }

    const revenueCanvas = document.getElementById("revenueChart");
    if (revenueCanvas && window.Chart) {
        new Chart(revenueCanvas, {
            type: "line",
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets: [{
                    label: "Revenue",
                    data: [12000, 18000, 15000, 25000, 22000, 30000],
                    borderColor: "#22C55E",
                    backgroundColor: "rgba(34, 197, 94, .12)",
                    borderWidth: 3,
                    tension: .42,
                    fill: true,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: "rgba(51, 65, 85, .45)" } },
                    y: { grid: { color: "rgba(51, 65, 85, .45)" } }
                }
            }
        });
    }

    const inventoryCanvas = document.getElementById("inventoryChart");
    if (inventoryCanvas && window.Chart) {
        new Chart(inventoryCanvas, {
            type: "doughnut",
            data: {
                labels: ["Electronics", "Accessories", "Office"],
                datasets: [{
                    data: [45, 30, 25],
                    backgroundColor: ["#22C55E", "#3B82F6", "#F59E0B"],
                    borderColor: "#1E293B",
                    borderWidth: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%"
            }
        });
    }
});
