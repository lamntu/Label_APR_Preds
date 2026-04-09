import os

import pandas as pd
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "annotation-secret"

DATA_PATH = "data/dataset.csv"
ANNOTATION_DIR = "data"
# ANNOTATION_PATH = "data/labels.csv"

dataset = pd.read_csv(DATA_PATH)


def get_annotation_path():
    annotator = session.get("annotator")
    return f"{ANNOTATION_DIR}/labels_{annotator}.csv"


def reload_annotations():
    path = get_annotation_path()

    if os.path.exists(path):
        annotations = pd.read_csv(path)
    else:
        annotations = pd.DataFrame(columns=["id", "score", "comment"])

    return annotations


@app.route("/", methods=["GET", "POST"])
def login():
    annotators = ["Lam", "Chenxi", "Haoye", "Xiaoning", "Aldeida"]

    if request.method == "POST":
        session["annotator"] = request.form["annotator"]
        return redirect("/records")

    return render_template("login.html", annotators=annotators)


@app.route("/records")
def index():
    if "annotator" not in session:
        return redirect("/")

    annotations = reload_annotations()
    annotated_ids = set(annotations["id"].tolist())

    show_pending_only = session.get("show_pending_only", False)

    records = []

    for i, row in dataset.iterrows():
        records.append({
            "idx": row["id"],
            "bug_id": row["bug_id"],
            "model": row["model"],
            "dataset": row["dataset"],
            "annotated": row["id"] in annotated_ids
        })

    records.sort(key=lambda x: x["bug_id"])

    for i, row in enumerate(records):
        row["row_num"] = i + 1

    return render_template(
        "index.html",
        records=records,
        total=len(dataset),
        annotated=len(annotated_ids),
        annotator=session["annotator"],
        show_pending_only=show_pending_only
    )


def remove_trailing(code):
    lines = code.split("\n")
    leading_spaces = len(lines[0]) - len(lines[0].lstrip(' '))
    lines = [l if len(l) < leading_spaces else l[leading_spaces:] for l in lines]
    return "\n".join(lines)


@app.route("/annotate/<int:idx>")
def annotate(idx):
    if "annotator" not in session:
        return redirect("/")

    row = dataset.iloc[idx]

    annotations = reload_annotations()
    existing = annotations[annotations["id"] == row["id"]]

    score = 3
    comment = ""

    if len(existing) > 0:
        score = existing.iloc[0]["score"]
        comment = existing.iloc[0]["comment"]
        if not isinstance(comment, str) or comment == None:
            comment = ""

    buggy = remove_trailing(row["buggy"])
    llm_fix = remove_trailing(row["patch"])
    try:
        dev_fix = remove_trailing(row["fix"])
    except:
        dev_fix = row["fix"]

    return render_template(
        "annotate.html",
        idx=idx,
        bug_id=row["bug_id"],
        buggy=buggy,
        dev_fix=dev_fix,
        llm_fix=llm_fix,
        bug_info=row["bug_info"],
        explanation=row["explanation"],
        score=score,
        comment=comment,
        annotator=session["annotator"]
    )


@app.route("/submit", methods=["POST"])
def submit():
    annotations = reload_annotations()
    path = get_annotation_path()

    data = request.json
    data["id"] = int(data["id"])

    new = pd.DataFrame([{
        "id": data["id"],
        "score": data["score"],
        "comment": data["comment"]
    }])

    if os.path.exists(path):
        old = pd.read_csv(path)
        old['id'] = old['id'].astype(int)
        old = old.loc[old["id"] != data["id"]]
        updated = pd.concat([old, new])
        updated.to_csv(path, index=False)
    else:
        new.to_csv(path, index=False)

    return {"status": "saved"}


@app.route("/set_pending_filter", methods=["POST"])
def set_pending_filter():
    data = request.json
    value = bool(data["value"])
    session["show_pending_only"] = value
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
