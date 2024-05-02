from flask import Flask, render_template, request, send_from_directory, send_file, jsonify, redirect, url_for
import os
import subprocess
from glob import glob
import zipfile
import tempfile
from zipfile import ZipFile
import glob

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_url', methods=['POST'])
def process_url():
    repository_url = request.form['repository_url']
    language = request.form['language']
    command = ['./scripts/query-setting.sh', repository_url, language]
    try:
        subprocess.Popen(command)
        return redirect(url_for('run_query'))
    except subprocess.CalledProcessError as e:
        print("CalledProcessError:", e)
        return render_template('index.html', error="Failed to start the process.")

@app.route('/check_process')
def check_process():
    codeql_status_file = "/home/codevuln/codeql_complete.txt"
    semgrep_status_file = "/home/codevuln/semgrep_complete.txt"
    if os.path.exists(codeql_status_file) and os.path.exists(semgrep_status_file):
        os.remove(codeql_status_file)
        os.remove(semgrep_status_file)
        return jsonify({"status": "complete", "redirect": url_for('ok')})
    else:
        return jsonify({}), 204

@app.route('/setting')
def settings():
    return render_template('setting.html')

@app.route('/run_query')
def run_query():
    return render_template('run_query.html')

def create_zip(files, directory):
    zip_filename = os.path.join(tempfile.gettempdir(), os.path.basename(directory) + '.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files:
            zipf.write(file, arcname=os.path.basename(file))
    return zip_filename

@app.route('/ok')
def ok():
    return render_template('ok.html')

@app.route('/download/scan_result', methods=['GET'])
def download_scan_result():
    try:
        with open('/home/codevuln/directory_name.txt', 'r') as file:
            directory_name = file.read().strip()
        
        directory_path = f"/home/codevuln/target-repo/{directory_name}/scan_result"
        
        files = glob.glob(os.path.join(directory_path, "*"))
        
        if not files:
            return "해당 디렉토리에 파일이 없습니다.", 404
        
        zip_path = f"/tmp/{directory_name}_scan_result.zip"
        with ZipFile(zip_path, 'w') as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        
        return send_file(zip_path, as_attachment=True, attachment_filename=f'{directory_name}_scan_result.zip')
    
    except Exception as e:
        return f"error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)