import unittest
import os
import time
import json
import importlib
from threading import Thread
from PIL import Image, ImageDraw
from unittest.mock import patch
import fakeredis

from api.app import app
from api import worker as worker_module

class TestApi(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.input_file = 'test_input.png'
        self.create_dummy_image(self.input_file, 100, 50, 'Test')

        # Set a small sleep time for the worker during tests
        os.environ['WORKER_SLEEP_TIME'] = '1'
        importlib.reload(worker_module)

        # Use a single fake redis instance for all patches
        fake_redis_instance = fakeredis.FakeRedis()

        # Patch the redis connection
        self.redis_patcher = patch('api.app.redis_conn', fake_redis_instance)
        self.redis_patcher.start()
        self.redis_patcher_worker = patch('api.worker.redis_conn', fake_redis_instance)
        self.redis_patcher_worker.start()
        self.redis_patcher_queue = patch('api.queue.redis_conn', fake_redis_instance)
        self.redis_patcher_queue.start()

        # Run the worker in a separate thread
        self.worker_thread = Thread(target=worker_module.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def tearDown(self):
        # Unset the environment variable
        del os.environ['WORKER_SLEEP_TIME']
        importlib.reload(worker_module)

        self.redis_patcher.stop()
        self.redis_patcher_worker.stop()
        self.redis_patcher_queue.stop()
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        # Clean up output files
        if os.path.exists('outputs'):
            for filename in os.listdir('outputs'):
                os.remove(os.path.join('outputs', filename))

    def create_dummy_image(self, filename, width, height, text):
        img = Image.new('RGB', (width, height), color = 'blue')
        d = ImageDraw.Draw(img)
        d.text((10,10), text, fill=(255,255,0))
        img.save(filename)

    def test_upload_and_conversion(self):
        # Test file upload
        with open(self.input_file, 'rb') as f:
            response = self.app.post('/upload', data={'file': (f, self.input_file)})

        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertIn('job_id', data)
        job_id = data['job_id']

        # Test job status
        response = self.app.get(f'/status/{job_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)

        # Wait for the conversion to complete
        for _ in range(10): # Timeout after 10 seconds
            response = self.app.get(f'/status/{job_id}')
            data = json.loads(response.data)
            if data['status'] == 'completed':
                break
            time.sleep(1)

        self.assertEqual(data['status'], 'completed')

        # Test getting the result
        response = self.app.get(f'/result/{job_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.decode('utf-8').startswith('<?xml version="1.0" encoding="utf-8" ?>'))
        self.assertTrue('<svg' in response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
