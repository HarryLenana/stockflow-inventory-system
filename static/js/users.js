// ======================================
// USER SEARCH
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("searchUser");

    if (!search) return;

    search.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        const rows = document.querySelectorAll("#userTable tr");

        rows.forEach(function (row) {

            const text = row.innerText.toLowerCase();

            if (text.includes(value)) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    });

});