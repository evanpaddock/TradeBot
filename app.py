from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


print(os.getenv("APP_KEY"))

if __name__ == "__main__":
    app.run()
