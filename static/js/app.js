console.log("StockFlow Premium Dashboard");

/* Animated Numbers */

const stats = document.querySelectorAll(".stat-card h2");

stats.forEach((stat) => {

    stat.style.opacity = "0";

    setTimeout(() => {

        stat.style.opacity = "1";
        stat.style.transition = "0.8s";

    }, 300);

});


/* Revenue Chart */

const revenueCanvas =
    document.getElementById("revenueChart");

if (revenueCanvas) {

    new Chart(revenueCanvas, {

        type: "line",

        data: {

            labels: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun"
            ],

            datasets: [{

                label: "Revenue",

                data: [
                    12000,
                    18000,
                    15000,
                    25000,
                    22000,
                    30000
                ],

                borderWidth: 3,
                tension: 0.4

            }]
        },

        options: {

            responsive: true,

            plugins: {
                legend: {
                    display: true
                }
            }

        }

    });

}


/* Inventory Chart */

const inventoryCanvas =
    document.getElementById("inventoryChart");

if (inventoryCanvas) {

    new Chart(inventoryCanvas, {

        type: "doughnut",

        data: {

            labels: [
                "Electronics",
                "Accessories",
                "Office"
            ],

            datasets: [{

                data: [
                    45,
                    30,
                    25
                ]

            }]
        },

        options: {

            responsive: true

        }

    });

}

const userBtn = document.getElementById("userBtn");
const userDropdown = document.getElementById("userDropdown");

if (userBtn) {

    userBtn.addEventListener("click", function (e) {

        e.stopPropagation();

        userDropdown.classList.toggle("show");

    });

}

window.addEventListener("click", function () {

    if (userDropdown) {

        userDropdown.classList.remove("show");

    }

});