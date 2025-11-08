import os
import time
import logging
from pixels2svg.main import pixels2svg
from api.job_queue import get_job_from_queue
import redis
import json

OUTPUT_FOLDER = os.path.abspath('outputs')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
redis_conn = redis.Redis(host=REDIS_HOST, port=6379, db=0)
WORKER_SLEEP_TIME = int(os.environ.get('WORKER_SLEEP_TIME', 60))

# Configure logging so logs show up in Docker and test output
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def worker():
    """The background worker that processes the conversion jobs."""
    logger.info('Worker started, waiting for jobs (brpop timeout=%s)', WORKER_SLEEP_TIME)
    while True:
        job = get_job_from_queue()
        if job:
            job_id = job['job_id']
            input_path = job['input_path']
            logger.info('Picked up job %s for input %s', job_id, input_path)

            # Update job status
            raw = redis_conn.get(job_id)
            if not raw:
                logger.error('Job metadata for %s not found in Redis', job_id)
                # Store an error state and continue
                redis_conn.set(job_id, json.dumps({'status': 'error', 'message': 'job metadata not found'}))
                continue

            try:
                job_data = json.loads(raw)
            except Exception as e:
                logger.exception('Failed to decode job metadata for %s: %s', job_id, e)
                redis_conn.set(job_id, json.dumps({'status': 'error', 'message': 'invalid job metadata'}))
                continue

            job_data['status'] = 'processing'
            redis_conn.set(job_id, json.dumps(job_data))

            # Get the original filename
            original_filename = "_".join(os.path.basename(input_path).split('_')[1:])
            output_filename = f"{job_id}_{os.path.splitext(original_filename)[0]}.svg"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            try:
                logger.info('Converting %s -> %s', input_path, output_path)
                pixels2svg(input_path=input_path, output_path=output_path)
                job_data['status'] = 'completed'
                job_data['output_path'] = output_path
                redis_conn.set(job_id, json.dumps(job_data))
                logger.info('Job %s completed, output at %s', job_id, output_path)
            except Exception as e:
                logger.exception('Job %s failed: %s', job_id, e)
                job_data['status'] = 'error'
                job_data['message'] = str(e)
                redis_conn.set(job_id, json.dumps(job_data))

        else:
            # No job returned within brpop timeout — loop and wait again
            logger.debug('No job received, continuing to wait...')
            # small sleep to avoid tight loop in environments where brpop uses very small timeout
            time.sleep(0.1)


if __name__ == '__main__':
    worker()
