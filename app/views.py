import json

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse

from .forms import ContactForm
from .models import LiveWin, Offer, PaymentMethod, SocialLink
import time
from django.shortcuts import render, redirect
from django.contrib import messages


def home(request):
    context = {
        'live_wins': LiveWin.objects.filter(visible=True).order_by('-timestamp')[:10],
        'active_offers': Offer.objects.filter(is_active=True),
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'social': SocialLink.objects.first(),
        'active_offer': Offer.get_upcoming_offer(),
        'contact_form': ContactForm(),  # Add form to context

    }
    return render(request, 'casino/index.html', context)


def contact_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
            return redirect('home')
    return redirect('home')


def updates(request):
    def event_stream():
        last_win_id = LiveWin.objects.last().id if LiveWin.objects.exists() else 0

        while True:
            # Send new live wins
            new_wins = LiveWin.objects.filter(id__gt=last_win_id)
            for win in new_wins:
                yield f"data: {json.dumps({'type': 'win', 'username': win.username, 'amount': str(win.amount)})}\n\n"
                last_win_id = win.id

            # Send updated offers countdown
            offers_data = [
                {
                    'id': offer.id,
                    'countdown': offer.time_remaining.total_seconds() if offer.time_remaining else 0

                    ()
                }
                for offer in Offer.objects.filter(is_active=True)
            ]
            yield f"data: {json.dumps({'type': 'offers', 'offers': offers_data})}\n\n"

            time.sleep(10)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


def subscribe(request):
    if request.method == 'POST':
        # Add validation and save logic
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
