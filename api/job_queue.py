import redis
import os

# Redis connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
redis_conn = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def add_job_to_queue(job_id, input_path):
    """Add a new job to the conversion queue."""
    redis_conn.rpush('conversion_queue', f"{job_id}:{input_path}")

def get_job_from_queue():
    """Get a job from the conversion queue."""
    job = redis_conn.lpop('conversion_queue')
    if job:
        job_id, input_path = job.decode('utf-8').split(':', 1)
        return {'job_id': job_id, 'input_path': input_path}
    return None
