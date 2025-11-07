import os
import time
from pixels2svg.main import pixels2svg
from api.job_queue import get_job_from_queue
import redis
import json

OUTPUT_FOLDER = os.path.abspath('outputs')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
redis_conn = redis.Redis(host=REDIS_HOST, port=6379, db=0)
WORKER_SLEEP_TIME = int(os.environ.get('WORKER_SLEEP_TIME', 60))

def worker():
    """The background worker that processes the conversion jobs."""
    while True:
        job = get_job_from_queue()
        if job:
            job_id = job['job_id']
            input_path = job['input_path']

            # Update job status
            redis_conn.set(job_id, json.dumps({'status': 'processing'}))

            # Get the original filename
            original_filename = "_".join(os.path.basename(input_path).split('_')[1:])
            output_filename = f"{job_id}_{os.path.splitext(original_filename)[0]}.svg"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            try:
                # Perform the conversion
                pixels2svg(input_path=input_path, output_path=output_path)
                redis_conn.set(job_id, json.dumps({'status': 'completed', 'output_path': output_path}))
            except Exception as e:
                redis_conn.set(job_id, json.dumps({'status': 'error', 'message': str(e)}))

        else:
            # If the queue is empty, wait for a short period before checking again
            time.sleep(WORKER_SLEEP_TIME)

if __name__ == '__main__':
    worker()
