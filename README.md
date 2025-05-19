# Django Rate Limiting Middleware

A Django middleware implementation that provides IP-based rate limiting functionality. This middleware tracks and limits the number of requests from each IP address within a rolling time window.

## Features

- IP-based rate limiting
- Rolling window implementation
- Configurable request limits and time windows
- Thread-safe implementation
- Rate limit headers in responses

## Requirements

- Python 3.x
- Django 4.x

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-directory>

2. Create and activate a virtual environment:

3. Install dependencies:
pip install -r requirements.txt

4. Apply migrations:
python manage.py makemigrations
python manage.py migrate

5. Run the development server:
python manage.py runserver

The middleware will be applied to all requests.

Configuration

The middleware is configured with the following default settings:

- Maximum requests: 100 per IP address
- Time window: 5 minutes (300 seconds)
  To modify these settings, adjust the values in core/middleware/rate_limit.py :
