import redis
import os

# Redis connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
redis_conn = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def add_job_to_queue(job_id, input_path):
    """Add a new job to the conversion queue."""
    redis_conn.rpush('conversion_queue', f"{job_id}:{input_path}")

def get_job_from_queue():
    """Get a job from the conversion queue using a blocking pop (brpop).

    Uses the `WORKER_SLEEP_TIME` environment variable as the brpop timeout (seconds).
    If no job is available within the timeout, returns None. This reduces busy
    polling compared to repeated lpop + sleep.
    """
    timeout = int(os.environ.get('WORKER_SLEEP_TIME', 60))
    # brpop returns a tuple (queue_name, item) or None on timeout
    result = redis_conn.brpop('conversion_queue', timeout=timeout)
    if result:
        _, job = result
        job_id, input_path = job.decode('utf-8').split(':', 1)
        return {'job_id': job_id, 'input_path': input_path}
    return None
