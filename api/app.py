import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import redis
import json
from datetime import datetime

from api.job_queue import add_job_to_queue

# Create the Flask application
app = Flask(__name__)

# Redis connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
redis_conn = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = os.path.abspath('uploads')
OUTPUT_FOLDER = os.path.abspath('outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the filename has a valid extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        job_id = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
        file.save(input_path)
        add_job_to_queue(job_id, input_path)
        redis_conn.set(job_id, json.dumps({'status': 'queued', 'timestamp': datetime.now().isoformat()}))
        redis_conn.sadd('job_ids', job_id)
        return jsonify({'job_id': job_id}), 202
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get the status of a job."""
    status = redis_conn.get(job_id)
    if status:
        return jsonify(json.loads(status))
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """Get the result of a job."""
    job_data = redis_conn.get(job_id)
    if job_data:
        job = json.loads(job_data)
        if job and job['status'] == 'completed':
            output_path = job.get('output_path')
            if output_path and os.path.exists(output_path):
                return send_from_directory(os.path.dirname(output_path), os.path.basename(output_path), as_attachment=True)
            else:
                return jsonify({'error': 'Output file not found'}), 404
        elif job:
            return jsonify({'status': job['status']}), 202
        else:
            return jsonify({'error': 'Job not found'}), 404
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/history', methods=['GET'])
def get_history():
    """Get the history of all jobs."""
    jobs = []
    job_ids = redis_conn.smembers('job_ids')
    for job_id in job_ids:
        job_data = redis_conn.get(job_id)
        if job_data:
            job = json.loads(job_data)
            job['job_id'] = job_id.decode('utf-8')
            jobs.append(job)
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True)
