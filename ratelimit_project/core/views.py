from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_endpoint(request):
    """
    A simple endpoint to test the rate limiting middleware.
    """
    return JsonResponse({
        'message': 'Request successful',
        'ip': request.META.get('REMOTE_ADDR'),
    })