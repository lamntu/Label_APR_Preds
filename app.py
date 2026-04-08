import random

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = "data/dataset.csv"
ANNOTATION_PATH = "data/labels.csv"

dataset = pd.read_csv(DATA_PATH)

def reload_annotations():
    if os.path.exists(ANNOTATION_PATH):
        annotations = pd.read_csv(ANNOTATION_PATH)
    else:
        annotations = pd.DataFrame(columns=["id", "score", "comment"])
    return annotations

annotations = reload_annotations()

@app.route("/")
def index():

    annotated_ids = set(annotations["id"].tolist())

    records = []

    for i, row in dataset.iterrows():
        records.append({
            "idx": row["id"],
            "bug_id": row["bug_id"],
            "model": row["model"],
            "dataset": row["dataset"],
            "annotated": row["id"] in annotated_ids
        })

    records.sort(key=lambda x : x["bug_id"])

    return render_template("index.html",
                           records=records,
                           total=len(dataset),
                           annotated=len(annotated_ids))

def remove_trailing(code):
    lines = code.split("\n")
    leading_spaces = len(lines[0]) - len(lines[0].lstrip(' '))
    lines = [l if len(l) < leading_spaces else l[leading_spaces:] for l in lines]
    return "\n".join(lines)

@app.route("/annotate/<int:idx>")
def annotate(idx):
    row = dataset.iloc[idx]

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
        comment=comment
    )


@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    data["id"] = int(data["id"])

    new = pd.DataFrame([{
        "id": data["id"],
        "score": data["score"],
        "comment": data["comment"]
    }])

    if os.path.exists(ANNOTATION_PATH):
        old = pd.read_csv(ANNOTATION_PATH)
        old['id'] = old['id'].astype(int)
        old = old.loc[old["id"] != data["id"]]
        updated = pd.concat([old, new])
        updated.to_csv(ANNOTATION_PATH, index=False)

    else:
        new.to_csv(ANNOTATION_PATH, index=False)

    global annotations
    annotations = reload_annotations()

    return {"status": "saved"}


if __name__ == "__main__":
    app.run(debug=True)