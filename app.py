import json
import re
import time
from urllib.parse import urlparse
from urllib.request import urlopen

import pandas as pd
from flask import Flask, render_template, request, redirect, session, jsonify
from sheets import save_annotation, load_annotations

app = Flask(__name__)
app.secret_key = "annotation-secret"

DATA_PATH = "data/dataset.csv"
ANNOTATION_DIR = "data"

dataset = pd.read_csv(DATA_PATH)

DEFAULT_FILTERS = {
    "search": "",
    "idx-lower": "",
    "idx-upper": "",
    "datasets": ["defects4j", "rwb", "swebench", "evalrepair-java", "evalrepair-cpp"],
    "systems": ["thinkrepair", "reinfix", "morepair"],
    "status": "all",
    "labels": ["incorrect", "unsure", "correct", ""]
}

def default_filters():
    return {key: value.copy() if isinstance(value, list) else value for key, value in DEFAULT_FILTERS.items()}

def same_record_id(left, right):
    return int(left) == int(right)


session_annotations = {}


def remember_annotations(annotator, annotations):
    session_annotations[annotator] = annotations


def current_annotations(annotator):
    if annotator not in session_annotations:
        session_annotations[annotator] = load_annotations(annotator)
    return session_annotations[annotator]


def find_remembered_annotation(record_id, annotator):
    return next(
        (annotation for annotation in current_annotations(annotator) if same_record_id(annotation["id"], record_id)),
        None
    )

def normalize_dataset(dataset_name):
    if str(dataset_name).startswith("d"):
        return "defects4j"
    if str(dataset_name).startswith("r"):
        return "rwb"
    return dataset_name


def build_records(annotator, annotations):
    annotated_ids = {int(x['id']): x for x in annotations}
    records = []

    for i, row in dataset.iterrows():
        bug_dataset = normalize_dataset(row["dataset"])

        label = "" if int(row["id"]) not in annotated_ids else annotated_ids[int(row["id"])]["label"]
        records.append({
            "idx": int(row["id"]),
            "bug_id": row["bug_id"],
            "model": row["model"],
            "dataset": bug_dataset,
            "annotated": int(row["id"]) in annotated_ids,
            "label": label
        })

    records.sort(key=lambda x: x["bug_id"])

    for i, row in enumerate(records):
        row["row_num"] = i + 1

    return records


@app.route("/", methods=["GET", "POST"])
def login():
    annotators = ["Annotator 1", "Annotator 2", "Annotator 3"]

    if request.method == "POST":
        session["annotator"] = request.form["annotator"]
        session["filters"] = default_filters()
        return redirect("/records")

    return render_template("login.html", annotators=annotators)


@app.route("/records")
def index():
    if "annotator" not in session:
        return redirect("/")

    annotator = session["annotator"]
    start_time = time.time()
    annotations = load_annotations(annotator)
    print("Load", time.time() - start_time)
    remember_annotations(annotator, annotations)

    filters = default_filters()
    filters.update(session.get("filters", {}))

    records = build_records(annotator, annotations)

    num_annotated = len([x for x in records if x["annotated"]])
    progress = 0 if len(records) == 0 else num_annotated / len(records) * 100
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
    code = code.replace("`", "")
    lines = code.split("\n")
    leading_spaces = len(lines[0]) - len(lines[0].lstrip(' '))
    lines = [l if len(l) < leading_spaces else l[leading_spaces:] for l in lines]
    return "\n".join(lines)

def clean_reinfix_expl(expl):
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


def extract_bug_report_url(dataset_name, bug_info):
    if not str(dataset_name).startswith("d"):
        return ""

    match = re.search(r"Bug report url:\s*(https?://\S+)", str(bug_info), re.IGNORECASE)
    return "" if match is None else match.group(1)


def is_json_bug_report_url(url):
    return urlparse(url).path.lower().endswith(".json")

@app.route("/annotate/<int:idx>")
def annotate(idx):
    if "annotator" not in session:
        return redirect("/")

    matching_rows = dataset[dataset["id"] == idx]
    if len(matching_rows) > 0:
        row = matching_rows.iloc[0]
    else:
        row = dataset.iloc[idx]

    if row["model"] == "reinfix":
        bug_id = row["bug_id"]
        if bug_id in ["Closure-28", "Chart-23"]:
            with open(f"data/{bug_id}_buggy.java", "r") as f:
                row["buggy"] = f.read()
            with open(f"data/{bug_id}_fix.java", "r") as f:
                row["fix"] = f.read()

    annotator = session["annotator"]
    existing = find_remembered_annotation(row["id"], annotator)

    label = "unsure"
    confidence = 5
    comment = ""
    annotated = existing is not None

    if annotated:
        label = existing["label"]
        confidence = existing["confidence"]
        comment = existing["comment"]
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
        if llm_fix[0] == '"' and llm_fix[-1] == '"':
            llm_fix = llm_fix[1:-1]

    bug_report_url = extract_bug_report_url(row["dataset"], row["bug_info"])
    bug_report_is_json = is_json_bug_report_url(bug_report_url) if bug_report_url else False

    return render_template(
        "annotate.html",
        idx=idx,
        bug_id=row["bug_id"],
        apr_system=row["model"],
        buggy=buggy,
        dev_fix=dev_fix,
        llm_fix=llm_fix,
        bug_info=row["bug_info"],
        bug_report_url=bug_report_url,
        bug_report_is_json=bug_report_is_json,
        explanation=expl,
        label=label,
        confidence=confidence,
        comment=comment,
        annotated=annotated,
        annotator=annotator,
        start_time=time.perf_counter()
    )


@app.route("/bug_report_json")
def bug_report_json():
    url = request.args.get("url", "")
    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        return {"error": "invalid url"}, 400

    if parsed_url.hostname != "storage.googleapis.com" or not is_json_bug_report_url(url):
        return {"error": "unsupported bug report url"}, 400

    try:
        with urlopen(url, timeout=8) as response:
            raw_data = response.read(2 * 1024 * 1024)
    except Exception:
        return {"error": "could not load bug report"}, 502

    try:
        return jsonify(json.loads(raw_data.decode("utf-8")))
    except Exception:
        return {"error": "invalid json"}, 502


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
    data = request.get_json(silent=True) or {}
    filters = default_filters()
    filters.update(data)
    session["filters"] = filters
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
