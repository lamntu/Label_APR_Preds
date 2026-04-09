window.onload = function() {
    // collapsible sections
    renderDiff(buggy, devfix, "devdiff")
    renderDiff(buggy, llmfix, "llmdiff")
//    hljs.highlightAll()

    console.log("Page is fully loaded.");
    document.querySelectorAll(".collapsible").forEach(btn => {
        btn.addEventListener("click", function() {
            this.classList.toggle("active");
            let content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
                this.textContent = "Show ▸";
            } else {
                content.style.display = "block";
                this.textContent = "Hide ▾";
            }
        });
    });
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

    console.log(diff)

    let html = Diff2Html.html(diff, {
        drawFileList: false,
        matching: "lines",
        outputFormat: "line-by-line"
    })

    document.getElementById(container).innerHTML = html
}

async function submitLabel() {
    let score = document.getElementById("score").value
    let comment = document.getElementById("comment").value

    await fetch("/submit", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            id: recordId,
            score: score,
            comment: comment
        })

    })

    alert("Saved!")
    window.location = '/records';
}