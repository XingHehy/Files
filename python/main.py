from flask import Flask, send_file, render_template, request, redirect, url_for

import os
import time
import datetime

app = Flask(__name__)
root_path = '../files'

def get_filesize(filesize):
    if filesize:
        if filesize > 1024**3:
            filesize = filesize / (1024**3)
            return f"{round(filesize, 2)} GB"

        elif filesize > 1024**2:
            filesize = filesize / (1024**2)
            return f"{round(filesize, 2)} MB"


        elif filesize > 1024 ** 1:
            filesize = filesize / 1024
            return f"{round(filesize, 2)} KB"
    else:
        return ""

def get_file_info(filename):
    filepath = os.path.join(root_path, filename)
    
    is_directory = os.path.isdir(filepath)
    timestamp = os.path.getmtime(filepath)
    if not is_directory:
        filesize = os.path.getsize(filepath)
    else:
        filesize = ""

    file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    return {
        'file': filename,
        'filename': os.path.basename(filename),
        'filesize': get_filesize(filesize),
        'is_directory': is_directory,
        'file_time': file_time
    }

@app.route('/')
def list_files():
    files_dir = root_path
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
    files = os.listdir(files_dir)
    files_info = [get_file_info(file) for file in files]
    folder_path = []
    current_path = ''
    for part in request.path.split('/')[1:]:
        current_path += '/' + part
        folder_path.append({
            'name': part,
            'href': current_path
        })
    return render_template('index.html', files_info=files_info, folder_path=folder_path)

@app.route('/<path:filepath>')
def handle_file(filepath):
    target_path = os.path.join(root_path, filepath)
    if os.path.isdir(target_path):
        files = os.listdir(target_path)
        files_info = [get_file_info(os.path.join(filepath, file)) for file in files]
        path = filepath.lstrip('/') if filepath else ''
        folder_path = []
        current_path = ''
        for part in request.path.split('/')[1:]:
            current_path += '/' + part
            folder_path.append({
                'name': part,
                'href': current_path
            })

        return render_template('index.html', files_info=files_info, folder_path=folder_path,path=path)
    else:
        if not os.path.exists(target_path):
            return render_template("404.html"), 404
        else:
            return send_file(target_path, as_attachment=True)


@app.route('/upload/', methods=['GET', 'POST'])
@app.route('/upload/<path:filepath>/', methods=['GET', 'POST'])
def upload_file(filepath=None):
    if request.method == 'POST':
        if filepath:
            all_path = os.path.join(root_path, filepath)
        else:
            all_path = root_path
            filepath = "" 
        file = request.files['file']
        if file:
            filename = file.filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}"
            file.save(os.path.join(all_path, new_filename))
            return redirect(url_for('list_files')+filepath)
    if not filepath:
        filepath = ""
    return render_template('upload.html',filepath=filepath)


@app.errorhandler(404)
def error_date(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0',port=8765)