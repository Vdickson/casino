# tasks.py (new file)
from celery import shared_task
from .models import UserInteraction, PageVisit
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import log_interaction, log_page_visit

@shared_task
def log_interaction(data):
    UserInteraction.objects.create(**data)

@shared_task
def log_page_visit(data):
    PageVisit.objects.create(**data)

# views.py
@csrf_exempt
def track_interaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            log_interaction.delay({
                'type': data.get('type'),
                'element_id': data.get('element_id'),
                'page_path': data.get('page_path', request.META.get('HTTP_REFERER', '/')),
                'additional_data': data.get('data', {})
            })
            return JsonResponse({'status': 'queued'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)