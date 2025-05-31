import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

@app.route("/", methods=["GET"])
def home():
    flash("Secret key is working!")
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
