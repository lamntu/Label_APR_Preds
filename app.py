import re
import time

import pandas as pd
from flask import Flask, render_template, request, redirect, session
from sheets import save_annotation, load_annotations

app = Flask(__name__)
app.secret_key = "annotation-secret"

DATA_PATH = "data/dataset.csv"
ANNOTATION_DIR = "data"
# ANNOTATION_PATH = "data/labels.csv"

dataset = pd.read_csv(DATA_PATH)


# def get_annotation_path():
#     annotator = session.get("annotator")
#     return f"{ANNOTATION_DIR}/labels_{annotator}.csv"
#
#
# def reload_annotations():
#     path = get_annotation_path()
#
#     if os.path.exists(path):
#         annotations = pd.read_csv(path)
#     else:
#         annotations = pd.DataFrame(columns=["id", "score", "comment"])
#
#     return annotations

# EQV_5 = ['Cli-17', 'Cli-25', 'Cli-28', 'Cli-4', 'Cli-40', 'Closure-159', 'Closure-168', 'Codec-18', 'Codec-3', 'Codec-5', 'Codec-9', 'Compress-14', 'Compress-19', 'Compress-27', 'Compress-31', 'Compress-32', 'Compress-7', 'Compress-8', 'Csv-1', 'Gson-11', 'JacksonCore-5', 'JacksonCore-6', 'JacksonDatabind-1', 'JacksonDatabind-16', 'JacksonDatabind-33', 'JacksonDatabind-70', 'JacksonDatabind-83', 'Jsoup-20', 'Jsoup-24', 'Jsoup-41', 'Jsoup-43', 'Jsoup-45', 'Jsoup-47', 'Jsoup-70', 'Jsoup-72', 'Jsoup-77', 'Jsoup-90', 'JxPath-22', 'JxPath-5', 'JxPath-8', 'Chart-1', 'Chart-11', 'Chart-13', 'Chart-3', 'Chart-4', 'Chart-5', 'Chart-7', 'Chart-9', 'Closure-1', 'Closure-104', 'Closure-105', 'Closure-107', 'Closure-11', 'Closure-113', 'Closure-114', 'Closure-115', 'Closure-116', 'Closure-117', 'Closure-118', 'Closure-119', 'Closure-120', 'Closure-121', 'Closure-126', 'Closure-128', 'Closure-13', 'Closure-130', 'Closure-131', 'Closure-14', 'Closure-15', 'Closure-17', 'Closure-18', 'Closure-19', 'Closure-21', 'Closure-22', 'Closure-23', 'Closure-25', 'Closure-29', 'Closure-32', 'Closure-35', 'Closure-36', 'Closure-38', 'Closure-39', 'Closure-40', 'Closure-44', 'Closure-5', 'Closure-50', 'Closure-51', 'Closure-52', 'Closure-53', 'Closure-56', 'Closure-57', 'Closure-58', 'Closure-59', 'Closure-61', 'Closure-62', 'Closure-65', 'Closure-67', 'Closure-69', 'Closure-71', 'Closure-73', 'Closure-77', 'Closure-78', 'Closure-81', 'Closure-83', 'Closure-86', 'Closure-88', 'Closure-91', 'Closure-92', 'Closure-95', 'Closure-96', 'Closure-99', 'Lang-10', 'Lang-11', 'Lang-12', 'Lang-17', 'Lang-19', 'Lang-22', 'Lang-28', 'Lang-31', 'Lang-33', 'Lang-37', 'Lang-39', 'Lang-40', 'Lang-42', 'Lang-43', 'Lang-45', 'Lang-48', 'Lang-5', 'Lang-51', 'Lang-52', 'Lang-54', 'Lang-59', 'Lang-6', 'Lang-61', 'Math-10', 'Math-101', 'Math-102', 'Math-106', 'Math-19', 'Math-21', 'Math-26', 'Math-28', 'Math-3', 'Math-30', 'Math-31', 'Math-32', 'Math-33', 'Math-41', 'Math-42', 'Math-44', 'Math-48', 'Math-5', 'Math-50', 'Math-51', 'Math-56', 'Math-57', 'Math-60', 'Math-69', 'Math-7', 'Math-72', 'Math-73', 'Math-79', 'Math-8', 'Math-80', 'Math-82', 'Math-84', 'Math-85', 'Math-86', 'Math-87', 'Math-88', 'Math-90', 'Math-91', 'Math-94', 'Math-95', 'Math-96', 'Math-97', 'Mockito-1', 'Mockito-13', 'Mockito-18', 'Mockito-22', 'Mockito-5', 'Mockito-8', 'Time-14', 'Time-15', 'Time-16', 'Time-17', 'Time-18', 'Time-19', 'Time-24', 'Time-25', 'Time-27', 'Time-4', 'Time-5', 'Time-7', 'Time-8', 'Cli-15', 'Cli-20', 'Cli-23', 'Cli-9', 'Closure-146', 'Closure-150', 'Closure-160', 'Closure-172', 'Closure-176', 'Codec-2', 'Compress-10', 'Compress-15', 'Compress-16', 'Compress-17', 'Compress-18', 'Compress-24', 'Compress-26', 'Compress-30', 'Csv-14', 'Gson-13', 'Gson-16', 'Gson-5', 'Gson-6', 'JacksonCore-15', 'JacksonCore-21', 'JacksonCore-25', 'JacksonDatabind-101', 'JacksonDatabind-102', 'JacksonDatabind-107', 'JacksonDatabind-17', 'JacksonDatabind-27', 'JacksonDatabind-45', 'JacksonDatabind-47', 'JacksonDatabind-51', 'JacksonDatabind-54', 'JacksonDatabind-62', 'JacksonDatabind-71', 'JacksonDatabind-76', 'JacksonDatabind-82', 'JacksonDatabind-85', 'JacksonDatabind-93', 'JacksonDatabind-97', 'Jsoup-39', 'Jsoup-46', 'Jsoup-50', 'Jsoup-59', 'Jsoup-84', 'Jsoup-93', 'JxPath-12']

BATCHES = {
    "Chenxi": ["Chart-1", "Chart-10", "Chart-11", "Chart-12", "Chart-13", "Chart-14", "Chart-15", "Chart-16", "Chart-17", "Chart-18", "Chart-19", "Chart-2", "Chart-20", "Chart-21", "Chart-22", "Chart-23", "Chart-24", "Chart-25", "Chart-26", "Chart-3", "Chart-4", "Chart-5", "Chart-6", "Chart-7", "Chart-8", "Chart-9", "Cli-10", "Cli-11", "Cli-12", "Cli-14", "Cli-15", "Cli-17", "Cli-18", "Cli-19", "Cli-2", "Cli-20", "Cli-23", "Cli-24", "Cli-25", "Cli-251", "Cli-253", "Cli-254", "Cli-257", "Cli-26", "Cli-27", "Cli-28", "Cli-29", "Cli-3", "Cli-30", "Cli-32", "Compress-37", "Compress-38", "Compress-39", "Compress-4", "Compress-40", "Compress-41", "Compress-43"],
    "Haoye": ["Cli-33", "Cli-35", "Cli-37", "Cli-38", "Cli-39", "Cli-4", "Cli-40", "Cli-5", "Cli-8", "Cli-9", "Closure-1", "Closure-10", "Closure-100", "Closure-101", "Closure-102", "Closure-103", "Closure-104", "Closure-105", "Closure-106", "Closure-107", "Closure-109", "Closure-11", "Closure-110", "Closure-111", "Closure-112", "Closure-113", "Closure-114", "Closure-115", "Closure-116", "Closure-117", "Closure-118", "Closure-119", "Closure-12", "Closure-120", "Closure-121", "Closure-122", "Closure-124", "Closure-125", "Closure-126", "Closure-127", "Closure-128", "Closure-129", "Closure-13", "Closure-130"],
    "Xiaoning": ["Closure-131", "Closure-132", "Closure-133", "Closure-136", "Closure-138", "Closure-14", "Closure-141", "Closure-142", "Closure-143", "Closure-145", "Closure-146", "Closure-147", "Closure-15", "Closure-150", "Closure-152", "Closure-156", "Closure-159", "Closure-160", "Closure-161", "Closure-164", "Closure-166", "Closure-167", "Closure-168", "Closure-17", "Closure-172", "Closure-174", "Closure-176", "Closure-18", "Closure-19", "Closure-2", "Closure-20", "Closure-21", "Closure-22", "Closure-23", "Closure-24", "Closure-25", "Closure-28", "Closure-29", "Closure-3", "Closure-31", "Closure-32", "Closure-33", "Closure-34", "Closure-35", "Closure-36", "Closure-37", "Closure-38", "Closure-39", "Closure-4", "Closure-40", "Closure-41", "Closure-42"],
    "Aldeida": ["Closure-44", "Closure-45", "Closure-47", "Closure-48", "Closure-49", "Closure-5", "Closure-50", "Closure-51", "Closure-52", "Closure-53", "Closure-54", "Closure-55", "Closure-56", "Closure-57", "Closure-58", "Closure-59", "Closure-60", "Closure-61", "Closure-62", "Closure-64", "Closure-65", "Closure-66", "Closure-67", "Closure-68", "Closure-69", "Closure-7", "Closure-70", "Closure-71", "Closure-72", "Closure-73", "Closure-75", "Closure-76", "Closure-77", "Closure-78", "Closure-79", "Closure-8", "Closure-81", "Closure-82", "Closure-83", "Closure-85", "Closure-86", "Closure-87", "Closure-88", "Closure-89", "Closure-9", "Closure-90", "Closure-91", "Closure-92", "Closure-94", "Closure-95", "Closure-96"],
    "Neelofar": ["Closure-97", "Closure-99", "Codec-10", "Codec-15", "Codec-159", "Codec-161", "Codec-163", "Codec-164", "Codec-166", "Codec-17", "Codec-18", "Codec-2", "Codec-3", "Codec-4", "Codec-5", "Codec-6", "Codec-7", "Codec-8", "Codec-9", "Collections-186", "Collections-25", "Collections-26", "Compress-1", "Compress-10", "Compress-11", "Compress-12", "Compress-13", "Compress-14", "Compress-15", "Compress-16", "Compress-17", "Compress-18", "Compress-19", "Compress-20", "Compress-21", "Compress-23", "Compress-24", "Compress-25", "Compress-26", "Compress-27", "Compress-28", "Compress-30", "Compress-31", "Compress-32", "Compress-34", "Compress-35", "Compress-36", "Compress-44", "Compress-45", "Compress-46", "Compress-5", "Compress-6", "Compress-7"]
}

@app.route("/", methods=["GET", "POST"])
def login():
    annotators = ["Lam", "Chenxi", "Haoye", "Xiaoning", "Aldeida", "Neelofar"]

    if request.method == "POST":
        session["annotator"] = request.form["annotator"]
        session["filters"] = {
            "idx-lower": "",
            "idx-upper": "",
            # "datasets": ["defects4j", "rwb", "swebench", "evalrepair-java", "evalrepair-cpp"],
            "datasets": ["defects4j", "rwb"],
            "systems": ["thinkrepair", "reinfix", "morepair"],
            "status": "all",
            "labels": ["incorrect", "unsure", "correct", ""]
        }
        return redirect("/records")

    return render_template("login.html", annotators=annotators)


@app.route("/records")
def index():
    if "annotator" not in session:
        return redirect("/")

    annotator = session["annotator"]
    annotations = load_annotations(annotator)
    annotated_ids = {x['id'] : x for x in annotations}

    filters = session.get("filters", {
        "idx-lower": "",
        "idx-upper": "",
        # "datasets": ["defects4j", "rwb", "swebench", "evalrepair-java", "evalrepair-cpp"],
        "datasets": ["defects4j", "rwb"],
        "systems": ["thinkrepair", "reinfix", "morepair"],
        "status": "all",
        "labels": ["incorrect", "unsure", "correct", ""]
    })

    # print(filters)

    records = []

    for i, row in dataset.iterrows():
        if row["dataset"].startswith("d"):
            bug_dataset = "defects4j"
        elif row["dataset"].startswith("r"):
            bug_dataset = "rwb"
        else:
            bug_dataset = row["dataset"]

        if annotator in BATCHES and (bug_dataset != "defects4j" or row["bug_id"] not in BATCHES[annotator]):
            continue

        label = "" if row["id"] not in annotated_ids else annotated_ids[row["id"]]["label"]
        records.append({
            "idx": row["id"],
            "bug_id": row["bug_id"],
            "model": row["model"],
            "dataset": bug_dataset,
            "annotated": row["id"] in annotated_ids,
            "label": label
        })

    records.sort(key=lambda x: x["bug_id"])

    for i, row in enumerate(records):
        row["row_num"] = i + 1

    # records = [x for x in records if x["model"]=="thinkrepair" and x["bug_id"] in EQV_5]
    num_annotated = len([x for x in records if x["annotated"]])
    progress = num_annotated / len(records) * 100
    progress = round(progress, 2)

    return render_template(
        "index.html",
        records=records,
        total=len(records),
        progress=progress,
        annotated=num_annotated,
        annotator=annotator,
        filters=filters
    )


def remove_trailing(code):
    # if not isinstance(code, str):
    #     return ""
    code = code.replace("`", "")
    lines = code.split("\n")
    leading_spaces = len(lines[0]) - len(lines[0].lstrip(' '))
    lines = [l if len(l) < leading_spaces else l[leading_spaces:] for l in lines]
    return "\n".join(lines)

def clean_reinfix_expl(expl):
    # expl = re.sub(r"```java\s*[\s\S]*?```", "", expl)
    def remove_java_blocks(match):
        content = match.group(1)
        # Count lines (ignore leading/trailing empty lines if needed)
        line_count = len(content.strip().splitlines())
        return "" if line_count > 5 else match.group(0)

    pattern = r"```java\s*\n([\s\S]*?)```"
    expl = re.sub(pattern, remove_java_blocks, expl)
    expl = expl.replace("Example fix:", "").replace("Example:", "").replace("Revised code:", "")
    if "Suggestion 2" in expl:
        expl = expl[:expl.index("Suggestion 2")]
    expl = expl.strip()
    if expl.endswith("###"):
        expl = expl[:-3].strip()
    return expl

@app.route("/annotate/<int:idx>")
def annotate(idx):
    if "annotator" not in session:
        return redirect("/")

    row = dataset.iloc[idx]

    annotator = session["annotator"]
    annotations = load_annotations(annotator)
    existing = [x for x in annotations if x["id"] == row["id"]]
    # annotations[annotations["id"] == row["id"]]

    label = "unsure"
    confidence = 5
    comment = ""
    annotated = len(existing) > 0

    if annotated:
        label = existing[0]["label"]
        confidence = existing[0]["confidence"]
        comment = existing[0]["comment"]
        if not isinstance(comment, str) or comment == None:
            comment = ""

    buggy = remove_trailing(row["buggy"])
    llm_fix = remove_trailing(row["patch"])
    try:
        dev_fix = remove_trailing(row["fix"])
    except:
        dev_fix = row["fix"]

    expl = row["explanation"]
    if row["model"] == "reinfix":
        expl = clean_reinfix_expl(expl)

    return render_template(
        "annotate.html",
        idx=idx,
        bug_id=row["bug_id"],
        buggy=buggy,
        dev_fix=dev_fix,
        llm_fix=llm_fix,
        bug_info=row["bug_info"],
        explanation=expl,
        label=label,
        confidence=confidence,
        comment=comment,
        annotated=annotated,
        annotator=annotator,
        start_time=time.perf_counter()
    )


@app.route("/submit", methods=["POST"])
def submit():
    end_time = time.perf_counter()

    data = request.json
    data["id"] = int(data["id"])

    start_time = data["startTime"]
    exec_time = end_time - start_time

    save_annotation(
        record_id=data["id"],
        annotator=session["annotator"],
        label=data["label"],
        confidence=data["confidence"],
        comment=data["comment"],
        exec_time=exec_time
    )

    return {"status": "saved"}


@app.route("/set_filters", methods=["POST"])
def set_filters():
    data = request.json
    session["filters"] = data
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
