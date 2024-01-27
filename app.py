from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save(file.filename)


if __name__ == '__main__':
    app.run()
