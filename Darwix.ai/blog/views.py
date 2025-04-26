from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .blogg import suggest_blog_titles

@csrf_exempt
def blog_suggest(request, title):
    if request.method == 'GET' and title:
        try:
            # Generate blog suggestions
            result = suggest_blog_titles(title)
            response = {
                'success':True,
                'result':result
            }
            return JsonResponse(response,safe=True)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method or missing title'
    }, status=400)
