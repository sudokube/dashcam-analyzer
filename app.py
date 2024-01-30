from flask import Flask
from flask import render_template
from flask import request
import subprocess
import uuid

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']

    if uploaded_file.filename != '':
        file_path = f'./upload/{str(uuid.uuid4()) + ".mp4"}'
        uploaded_file.save(file_path)

        subprocess.run(['python', './modules/lane/P4.py', file_path])

        module_path = './modules/going/detect.py'
        project_path = './download'
        weights_path = './modules/going/runs/train/exp12/weights/best.pt'

        command = f'python {module_path} --project {project_path} --source {file_path} --weights {weights_path}'
        subprocess.run(command, shell=True)


if __name__ == '__main__':
    app.run()
