from django.core.cache import cache
from django.http import HttpResponse
import time
import threading

class RateLimitMiddleware:
    """
    Middleware that implements IP-based rate limiting.
    Limits requests to 100 per IP address in a rolling 5-minute window.
    """
    
    # Lock for thread safety when updating shared data
    _lock = threading.Lock()
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # Maximum requests allowed
        self.time_window = 300  # 5 minutes in seconds
        
    def __call__(self, request):
        # Get client IP address
        ip_address = self._get_client_ip(request)
        
        # Check if the IP is rate limited
        is_limited, remaining, reset_time = self._check_rate_limit(ip_address)
        
        if is_limited:
            # Return 429 Too Many Requests response
            response = HttpResponse(
                "Rate limit exceeded. Try again later.",
                status=429
            )
        else:
            # Process the request normally
            response = self.get_response(request)
        
        # Add rate limit headers to the response
        response['X-RateLimit-Limit'] = str(self.rate_limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(reset_time)
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        Handles cases where the request might be behind a proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the client IP (first in the list)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_rate_limit(self, ip_address):
        """        
        Check if the IP address has exceeded the rate limit.
        Returns a tuple of (is_limited, remaining_requests, reset_time).
        
        Implements a rolling window approach using timestamps of requests.
        """
        cache_key = f"ratelimit:{ip_address}"
        current_time = int(time.time())
        window_start_time = current_time - self.time_window
        
        # Get the existing request timestamps for this IP
        with self._lock:
            request_timestamps = cache.get(cache_key, [])
            
            # Filter out timestamps outside the current window
            request_timestamps = [ts for ts in request_timestamps if ts >= window_start_time]
            
            # Count requests in the current window
            request_count = len(request_timestamps)
            
            # Calculate remaining requests BEFORE adding the current request
            remaining = max(0, self.rate_limit - request_count - 1)  # Subtract 1 for current request
            
            # Check if rate limit is exceeded
            is_limited = request_count >= self.rate_limit
            
            if not is_limited:
                # Add current timestamp to the list
                request_timestamps.append(current_time)
                
            # Store updated timestamps back in cache
            # Set expiration to the time window to automatically clean up old entries
            cache.set(cache_key, request_timestamps, self.time_window)
        
        reset_time = window_start_time + self.time_window
        
        return is_limited, remaining, reset_time