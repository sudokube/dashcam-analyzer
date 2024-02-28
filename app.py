import pickle

from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from moviepy.editor import VideoFileClip

import cv2
import os
import subprocess
import uuid

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']

    if uploaded_file.filename != '':
        file_id = str(uuid.uuid4())
        file_path = f'./upload/{file_id}.mp4'
        uploaded_file.save(file_path)

        subprocess.run(['python', './modules/lane/P4.py', file_path])

        module_path = './modules/going/detect.py'
        project_path = './upload'
        weights_path = './modules/going/runs/train/exp12/weights/best.pt'

        command = f'python {module_path} --project {project_path} --source {file_path[:-4] + "P4.mp4"} --weights {weights_path}'
        subprocess.run(command, shell=True)

        with open(f'{file_path[:-4]}.pkl', 'rb') as f:
            data = pickle.load(f)

        # Get fps
        cap = cv2.VideoCapture(file_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()

        with open(f'{file_path[:-4]}.txt', 'rb') as f:
            path = pickle.load(f)

        subclip_duration = 10

        with open(f'{file_path[:-4]}P4.pkl', 'rb') as f:
            idx = 0
            while idx < len(data):
                try:
                    lanes = pickle.load(f)
                except EOFError:
                    break

                frame = data[idx]

                for wheels in frame:
                    if wheels[0] < lanes[0] < wheels[1] or wheels[0] < lanes[1] < wheels[1]:
                        begin_frame = max(0, idx - subclip_duration * fps // 2)
                        end_frame = min(len(data) - 1, idx + subclip_duration * fps // 2)

                        begin = begin_frame / fps
                        end = end_frame / fps

                        source = VideoFileClip(path)

                        # Create subclip
                        subclip = source.subclip(begin, end)

                        # Export subclip
                        subclip_filename = f'{file_path[:17]}_subclip_{idx}.mp4'
                        subclip.write_videofile(subclip_filename, codec='libx264')

                        idx += fps * 5

                        for _ in range(fps * 5):
                            try:
                                lanes = pickle.load(f)
                            except EOFError:
                                break
                else:
                    idx += 1
        return file_id


@app.route('/subclips', methods=['GET'])
def subclips():
    uuid = request.args.get('resp')

    subclips = [f'video/{f}' for f in os.listdir('./upload') if f.startswith(f'{uuid}_subclip_') and f.endswith('mp4')]
    return render_template('subclips.html', subclips=subclips)


@app.route('/video/<subclip>')
def video(subclip):
    return send_file('upload/' + subclip)


if __name__ == '__main__':
    app.run()
