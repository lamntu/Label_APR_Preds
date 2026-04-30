window.onload = function() {
    applyFilters()
}

function applyProgress() {
    let rows = document.querySelectorAll("table>tbody>tr");
    let total_num = Array.from(rows).filter(row => row.style.display != "none").length;
    let annotated_num = Array.from(rows).filter(row => row.style.display != "none" && row.cells[4].textContent.includes("✔")).length;
    let annotated_num_txt = document.getElementById("annotated_num")
    let total_num_txt = document.getElementById("total_num")
    total_num_txt.innerHTML = total_num
    annotated_num_txt.innerHTML = annotated_num
    let progress_txt = document.getElementById("progress")
    progress_txt.innerHTML = (annotated_num / total_num * 100).toFixed(2);
}

function applyFilters() {
    let idFilterLower = document.getElementById("filter-idx-lower").value.toLowerCase();
    idFilterLower = Number(idFilterLower)
    let idFilterUpper = document.getElementById("filter-idx-upper").value.toLowerCase();
    idFilterUpper = Number(idFilterUpper)

    let statusFilter = document.getElementById("filter-status").value;

    // get selected datasets
    let checkedDatasetBoxes = document.querySelectorAll("#filter-dataset input:checked");
    let selectedDatasets = Array.from(checkedDatasetBoxes).map(cb => cb.value);

    // get selected systems
    let checkedSystemBoxes = document.querySelectorAll("#filter-system input:checked");
    let selectedSystems = Array.from(checkedSystemBoxes).map(cb => cb.value);

    // get selected labels
    let checkedLabelBoxes = document.querySelectorAll("#filter-label input:checked");
    let selectedLabels = Array.from(checkedLabelBoxes).map(cb => cb.value);

    let rows = document.querySelectorAll("table>tbody>tr");

    rows.forEach(row => {
        let cellTexts = Array.from(row.cells).map(cell => cell.textContent.trim().toLowerCase());
        let id =  Number(cellTexts[0]);
        let dataset = cellTexts[2];
        let apr = cellTexts[3];
        let status = cellTexts[4];
        let label = cellTexts[5];

        let show = true;

        if (idFilterUpper && idFilterLower) {
            if (id < idFilterLower || id > idFilterUpper) {
                show = false;
            }
        } else if (idFilterUpper) {
            if (id > idFilterUpper) {
                show = false;
            }
        } else if (idFilterLower) {
            if (id < idFilterLower) {
                show = false;
            }
        }

        if (statusFilter && statusFilter !== "all" && !status.includes(statusFilter)) {
            show = false;
        }

        // dataset filter (multi-select)
        if (!selectedDatasets.includes(dataset)) {
            show = false;
        }

        // system filter (multi-select)
        if (!selectedSystems.includes(apr)) {
            show = false;
        }

        // label filter (multi-select)
        if (!selectedLabels.includes(label)) {
            show = false;
        }

        row.style.display = show ? "" : "none";
    });

    applyProgress()
}

function submitFilters() {
    applyFilters()

    let idFilterLower = document.getElementById("filter-idx-lower").value.toLowerCase();
    let idFilterUpper = document.getElementById("filter-idx-upper").value.toLowerCase();

    let statusFilter = document.getElementById("filter-status").value;

    // get selected datasets
    let checkedDatasetBoxes = document.querySelectorAll("#filter-dataset input:checked");
    let selectedDatasets = Array.from(checkedDatasetBoxes).map(cb => cb.value);

    // get selected systems
    let checkedSystemBoxes = document.querySelectorAll("#filter-system input:checked");
    let selectedSystems = Array.from(checkedSystemBoxes).map(cb => cb.value);

    // get selected labels
    let checkedLabelBoxes = document.querySelectorAll("#filter-label input:checked");
    let selectedLabels = Array.from(checkedLabelBoxes).map(cb => cb.value);

    fetch("/set_filters", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "idx-lower": idFilterLower,
            "idx-upper": idFilterUpper,
            "datasets": selectedDatasets,
            "systems": selectedSystems,
            "status": statusFilter,
            "labels": selectedLabels
        })
    });
}

function clearFilters() {
    document.getElementById("filter-idx-lower").value = "";
    document.getElementById("filter-idx-upper").value = "";
    document.getElementById("filter-status").value = "all";

    document.querySelectorAll("#filter-dataset input")
        .forEach(cb => {
            if (!cb.disabled) {
                cb.checked = true
            }
        });

    document.querySelectorAll("#filter-system input")
        .forEach(cb => cb.checked = true);

    document.querySelectorAll("#filter-label input")
            .forEach(cb => cb.checked = true);

    applyFilters();

    fetch("/set_filters", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "idx-lower": "",
            "idx-upper": "",
//            "datasets": ["defects4j", "rwb", "swebench", "evalrepair-java", "evalrepair-cpp"],
            "datasets": ["defects4j", "rwb"],
            "systems": ["thinkrepair", "reinfix", "morepair"],
            "status": "all",
            "labels": ["incorrect", "unsure", "correct", ""]
        })
    });
}
