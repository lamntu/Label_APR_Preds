window.onload = function() {
    togglePendingFilter();
}

function togglePendingFilter() {
    const toggle = document.getElementById("pendingToggle");
    const rows = document.querySelectorAll("table tr");

    rows.forEach(row => {

        if (row.classList.contains("annotated")) {
            row.style.display = toggle.checked ? "none" : "";
        }

    });

    fetch("/set_pending_filter", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            value: toggle.checked
        })
    });
}