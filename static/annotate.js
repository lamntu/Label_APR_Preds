window.onload = function() {
    renderDiff(buggy, devfix, "devdiff")
    renderDiff(buggy, llmfix, "llmdiff")
    initializeSliders()
    initializeBugReportJson()
    initializeTutorial()

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

function initializeTutorial() {
    document.getElementById("tutorial-toggle").addEventListener("click", toggleTutorial);
    document.getElementById("tutorial-close").addEventListener("click", hideTutorial);
    document.querySelectorAll(".manual-step").forEach(step => {
        step.addEventListener("click", navigateToManualTarget);
    });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            hideTutorial();
        }
    });
}

function toggleTutorial() {
    let panel = document.getElementById("tutorial-panel");
    if (panel.hidden) {
        showTutorial();
    } else {
        hideTutorial();
    }
}

function showTutorial() {
    let panel = document.getElementById("tutorial-panel");
    let toggle = document.getElementById("tutorial-toggle");

    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
}

function hideTutorial() {
    let panel = document.getElementById("tutorial-panel");
    let toggle = document.getElementById("tutorial-toggle");

    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
}

function navigateToManualTarget(event) {
    let target = document.getElementById(event.currentTarget.dataset.target);
    if (!target) {
        return;
    }

    if (target.id === "llm-fix-section") {
        showLlmFixSection(target);
    }

    target.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
    highlightSection(target);
}

function showLlmFixSection(section) {
    let toggle = section.querySelector(".collapsible");
    let content = section.querySelector(".content");

    if (toggle && content && content.style.display !== "block") {
        toggle.classList.add("active");
        toggle.textContent = "Hide";
        content.style.display = "block";
    }
}

function highlightSection(section) {
    document.querySelectorAll(".section-highlight").forEach(element => {
        element.classList.remove("section-highlight");
    });

    section.classList.add("section-highlight");
    window.setTimeout(() => {
        section.classList.remove("section-highlight");
    }, 1800);
}

async function initializeBugReportJson() {
    let reportContainer = document.getElementById("bug-report-json");
    if (!reportContainer) {
        return;
    }

    document.getElementById("bug-report-toggle").addEventListener("click", toggleBugReportJson);
}

async function toggleBugReportJson() {
    let reportContainer = document.getElementById("bug-report-json");
    let toggle = document.getElementById("bug-report-toggle");

    if (!reportContainer.hidden) {
        reportContainer.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        return;
    }

    reportContainer.hidden = false;
    toggle.setAttribute("aria-expanded", "true");

    if (reportContainer.dataset.loaded === "true") {
        return;
    }

    try {
        let response = await fetch(`/bug_report_json?url=${encodeURIComponent(reportContainer.dataset.url)}`);
        if (!response.ok) {
            throw new Error("Bug report unavailable");
        }

        renderBugReportJson(reportContainer, await response.json());
        reportContainer.dataset.loaded = "true";
    } catch (error) {
        reportContainer.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
    }
}

function renderBugReportJson(container, report) {
    container.innerHTML = "";

    let title = document.createElement("h3");
    title.textContent = report.summary || `Bug report ${report.id || ""}`.trim();
    container.appendChild(title);

    let meta = document.createElement("div");
    meta.className = "bug-report-meta";
    addMetaPill(meta, `ID ${report.id}`);
    addMetaPill(meta, report.status);
    addMetaPill(meta, `${report.stars || 0} stars`);
    addMetaPill(meta, `${report.commentCount || (report.comments || []).length} comments`);
    container.appendChild(meta);

    if (Array.isArray(report.labels) && report.labels.length > 0) {
//        let labels = document.createElement("div");
//        labels.className = "bug-report-labels";
        report.labels.forEach(label => addMetaPill(meta, label));
//        container.appendChild(labels);
    }

    if (Array.isArray(report.comments) && report.comments.length > 0) {
        let comments = document.createElement("div");
        comments.className = "bug-report-comments";
        report.comments.forEach(comment => comments.appendChild(renderBugReportComment(comment)));
        container.appendChild(comments);
    }
}

function renderBugReportComment(comment) {
    let article = document.createElement("article");
    article.className = "bug-report-comment";

    let heading = document.createElement("div");
    heading.className = "bug-report-comment-heading";
    heading.textContent = `Comment ${comment.id}`;

    if (comment.timestamp) {
        let timestamp = document.createElement("span");
        timestamp.textContent = new Date(comment.timestamp * 1000).toLocaleString();
        heading.appendChild(timestamp);
    }

    let content = document.createElement("pre");
    content.textContent = htmlToText(comment.content || "");

    article.appendChild(heading);
    article.appendChild(content);
    return article;
}

function addMetaPill(container, value) {
    if (value === undefined || value === null || value === "") {
        return;
    }

    let pill = document.createElement("span");
    pill.textContent = value;
    container.appendChild(pill);
}

function htmlToText(html) {
    let tmp = document.createElement("div");
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || "";
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
