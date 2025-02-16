from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
import requests
import json

from .models import Concert, Market
import credentials

"""
Fetch concerts from the Ticketmaster API matching the given parameters and add them to the concerts table.
"""
@csrf_exempt
@require_POST
def fetch_concerts(request):
    if request.body:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        body = {}

    # Construct the URL and parameters
    params = {
        'apikey': credentials.TICKETMASTER_API_KEY,
        'countryCode': "US",
        'classificationName': "music",
        'size': 200,
        'sort': 'date,name,asc'
    }
    if 'startDateTime' in body:
        params['startDateTime'] = body['startDateTime']
    if 'endDateTime' in body:
        params['endDateTime'] = body['endDateTime']
    if 'size' in body:
        params['size'] = body['size']
    if 'page' in body:
        params['page'] = body['page']
    market_id = body.get('marketId', 11)
    try:
        market = Market.objects.get(pk=market_id)
        params['marketId'] = market_id
    except Market.DoesNotExist:
        return JsonResponse({'error': 'Market does not exist'}, status=404)

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        concerts_data = response.json()
        unique_events = find_unique_events(concerts_data['_embedded']['events'])

        concerts_added = []
        with transaction.atomic():
            for event in unique_events:
                concert, created = create_or_update_concert(event, market_id)
                if created:
                    concerts_added.append(concert)
    
        return JsonResponse([concert.attraction_name for concert in concerts_added], safe=False)
    else:
        error_message = f"Failed to fetch concerts data: {response.text}"
        raise Exception(error_message)
    
def get_concerts(request):
    today = timezone.now().date()
    concerts = Concert.objects.filter(local_date__gte=today).values().order_by('local_date')
    return JsonResponse(list(concerts), safe=False)
 

def get_markets(request):
    markets = Market.objects.values()
    return JsonResponse(list(markets), safe=False)

"""
Filter out duplicate events (sometimes deluxe packages are shown as separate Events. we keep the one with the shorter name.)
"""
def find_unique_events(events):
    sorted_events = sorted(events, key=lambda x: (x['name'].lower(), len(x['name'])))
    unique_events = []
    seen_ids = set()
    for event in sorted_events:
        if '_embedded' in event and 'attractions' in event['_embedded'] and len(event['_embedded']['attractions']) > 0:
            attraction_id = event['_embedded']['attractions'][0]['id']
            if attraction_id not in seen_ids:
                unique_events.append(event)
                seen_ids.add(attraction_id)

    return unique_events

def create_or_update_concert(event, market_id):
    defaults={
        'name': event['name'],
        'url': event['url'],
        'image_url': find_largest_image(event['images'])['url'],
        'attraction_id': event['_embedded']['attractions'][0]['id'],
        'attraction_name': event['_embedded']['attractions'][0]['name'],
        'local_date': event['dates']['start']['localDate'],
        'local_time': event.get('dates', {}).get('start', {}).get('localTime', None),                    
        'genre': event['classifications'][0]['genre']['name'],
        'subgenre': event['classifications'][0]['subGenre']['name'],
        'market_id': market_id,
        'min_price': event.get('priceRanges', [{}])[0].get('min', None),
        'max_price': event.get('priceRanges', [{}])[0].get('max', None),
        'venue': event['_embedded']['venues'][0]['name'],
        'city': event['_embedded']['venues'][0]['city']['name'],
        'state': event['_embedded']['venues'][0]['state']['stateCode'],
    }
    if 'description' in event:
        defaults['description'] = event['description']
    elif 'info' in event:
        defaults['description'] = event['info']
    elif 'pleaseNote' in event:
        defaults['description'] = event['pleaseNote']

    return Concert.objects.update_or_create(
        event_id=event['id'],
        defaults=defaults
    )

def find_largest_image(images):
    return max(images, key=lambda image: image['width'] * image['height'], default=None)