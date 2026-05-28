window.onload = function() {
    renderDiff(buggy, devfix, "devdiff")
    renderDiff(buggy, llmfix, "llmdiff")
    initializeSliders()

    document.querySelectorAll(".collapsible").forEach(btn => {
        btn.addEventListener("click", function() {
            this.classList.toggle("active");
            let content = this.closest(".review-section").querySelector(".content");
            if (content.style.display === "block") {
                content.style.display = "none";
                this.textContent = "Show";
            } else {
                content.style.display = "block";
                this.textContent = "Hide";
            }
        });
    });

    document.getElementById("comment").addEventListener("input", clearSaveStatus);
}

const labelValues = ["incorrect", "unsure", "correct"];

function initializeSliders() {
    let labelSlider = document.getElementById("label-slider");
    let confidenceSlider = document.getElementById("confidence");

    updateLabelSlider();
    updateConfidenceSlider();

    labelSlider.addEventListener("input", updateLabelSlider);
    labelSlider.addEventListener("change", clearSaveStatus);
    confidenceSlider.addEventListener("input", updateConfidenceSlider);
    confidenceSlider.addEventListener("change", clearSaveStatus);
}

function updateLabelSlider() {
    let labelSlider = document.getElementById("label-slider");
    let label = labelValues[Number(labelSlider.value)];

    document.getElementById("label").value = label;
    document.getElementById("label-value").textContent = label;
    labelSlider.setAttribute("aria-valuetext", label);
    setSliderProgress(labelSlider);
}

function updateConfidenceSlider() {
    let confidenceSlider = document.getElementById("confidence");

    document.getElementById("confidence-value").textContent = confidenceSlider.value;
    setSliderProgress(confidenceSlider);
}

function setSliderProgress(slider) {
    let min = Number(slider.min);
    let max = Number(slider.max);
    let value = Number(slider.value);
    let progress = ((value - min) / (max - min)) * 100;

    slider.style.setProperty("--slider-progress", `${progress}%`);
}

function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}

function renderDiff(oldCode, newCode, container) {
    let diff = newCode.startsWith("diff --git") ? newCode : Diff.createTwoFilesPatch(
        "Buggy",
        "Fixed",
        oldCode,
        newCode
    )

    diff = decodeHtml(diff)

    let html = Diff2Html.html(diff, {
        drawFileList: false,
        matching: "lines",
        outputFormat: "line-by-line"
    })

    document.getElementById(container).innerHTML = html
}

async function submitLabel() {
    let label = document.getElementById("label").value
    let confidence = document.getElementById("confidence").value
    let comment = document.getElementById("comment").value
    let saveButton = document.getElementById("save-button")
    let saveStatus = document.getElementById("save-status")

    saveButton.disabled = true;
    saveButton.textContent = "Saving";
    saveStatus.textContent = "";

    try {
        let response = await fetch("/submit", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                id: recordId,
                label: label,
                confidence: confidence,
                comment: comment,
                startTime: startTime
            })
        })

        if (!response.ok) {
            throw new Error("Save failed");
        }

        saveStatus.textContent = "Saved. Returning to list...";
        window.location = '/records';
    } catch (error) {
        saveButton.disabled = false;
        saveButton.textContent = "Save";
        saveStatus.textContent = "Could not save. Please try again.";
    }
}

function clearSaveStatus() {
    document.getElementById("save-status").textContent = "";
}
