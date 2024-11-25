import os
from flask import Flask, render_template, request, session
from main import process_question

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        question = request.form["question"]
        result = process_question(question)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
