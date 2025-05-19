from django.test import TestCase, Client
from django.core.cache import cache
import time

class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        self.client = Client(REMOTE_ADDR='127.0.0.1')
        self.url = '/api/test/'
    
    def test_rate_limit_not_exceeded(self):
        # Make a request and check response
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        # Check rate limit headers
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Reset', response)
        
        # Verify remaining count is decremented
        self.assertEqual(response['X-RateLimit-Limit'], '100')
        self.assertEqual(response['X-RateLimit-Remaining'], '99')
    
    def test_rate_limit_exceeded(self):
        # Simulate 100 requests
        for i in range(100):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
        
        # The 101st request should be rate limited
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response['X-RateLimit-Remaining'], '0')
    
    def test_rolling_window(self):
        # This test is a simplified version since we can't wait 5 minutes in a unit test
        # In a real test, you might use time mocking libraries
        
        # Simulate the cache directly for this test
        ip = '127.0.0.1'
        cache_key = f"ratelimit:{ip}"
        
        # Set up timestamps that are just at the edge of the window
        current_time = int(time.time())
        window_size = 300  # 5 minutes
        
        # Create 99 old requests (just inside the window)
        old_timestamps = [current_time - window_size + 1] * 99
        cache.set(cache_key, old_timestamps, window_size)
        
        # The next request should succeed (100th request)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-RateLimit-Remaining'], '0')
        
        # The next request should fail (101st request)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 429)