// =====================================
// SmartSan JavaScript
// =====================================

console.log("SmartSan System Loaded");


// =====================================
// REPORT PAGE - ISSUE SELECTION
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    const issueButtons = document.querySelectorAll(".issue-btn");

    issueButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            issueButtons.forEach(function (btn) {
                btn.classList.remove("active");
            });

            button.classList.add("active");

        });

    });

});


// =====================================
// SUBMIT REPORT
// =====================================

async function submitReport() {

    const location = document.getElementById("location");

    const selectedIssue = document.querySelector(".issue-btn.active");

    const details = document.getElementById("description");

    if (!location || location.value === "") {
        alert("Please select a location.");
        return;
    }

    if (!selectedIssue) {
        alert("Please select an issue.");
        return;
    }

    const issueType = selectedIssue.textContent.trim();

    let priority = "MEDIUM";

    if (issueType.includes("Water Leakage") ||
        issueType.includes("Bad Smell")) {

        priority = "HIGH";

    }

    const reportData = {

        location_id: Number(location.value),

        issue_type: issueType,

        source: "QR",

        priority: priority,

        details: details ? details.value : ""

    };

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/complaints",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(reportData)
            }
        );

        const result = await response.json();

        if (response.ok) {

            alert(
                "Report submitted successfully! ✅\n" +
                "Complaint ID: " + result.complaint_id
            );

            if (details) {
                details.value = "";
            }

            document.querySelectorAll(".issue-btn").forEach(function (btn) {
                btn.classList.remove("active");
            });

        } else {

            alert("Error: " + result.message);

        }

    } catch (error) {

        console.error(error);

        alert(
            "Could not connect to SmartSan backend.\n" +
            "Please make sure Flask is running."
        );

    }

}


// =====================================
// STAFF DASHBOARD
// =====================================

function updateStatus(button) {

    const row = button.closest(".report-row");

    const status = row.querySelector(".status");

    if (status.classList.contains("pending")) {

        status.classList.remove("pending");
        status.classList.add("progress");

        status.textContent = "In Progress";

        button.textContent = "Complete";

        alert("Cleaning task started successfully! 🔄");

    }

    else if (status.classList.contains("progress")) {

        status.classList.remove("progress");
        status.classList.add("resolved");

        status.textContent = "Resolved";

        button.textContent = "Done ✓";

        button.classList.add("completed");

        button.disabled = true;

        alert("Cleaning task completed successfully! ✅");

    }

}


// =====================================
// REFRESH
// =====================================

function refreshReports() {

    alert("Dashboard refreshed successfully! 🔄");

    console.log("SmartSan reports refreshed");

}