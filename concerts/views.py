import requests
import json
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize

from .models import Concert, Market
import credentials

"""
Hit events endpoint and collect attraction IDs and artist names
"""

def get_concerts(request):
    # Define API parameters
    api_key = credentials.TICKETMASTER_API_KEY
    country_code = "US"
    market_id = 11
    classification_name = "music"
    size = 200

    # Construct the URL and parameters
    params = {
        'countryCode': country_code,
        'apikey': api_key,
        'marketId': market_id,
        'classificationName': classification_name,
        'size': size,
    }
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    # Make the API call
    response = requests.get(url, params=params)
    if response.status_code == 200:
        concerts_data = response.json()

        # Process the 'events' array inside '_embedded'
        events_array = concerts_data['_embedded']['events']

        # Sort and filter events as per the original JavaScript logic
        # Note: Python's sorting is stable, so we can sort by name and then by length if needed directly
        sorted_events = sorted(events_array, key=lambda x: (x['name'].lower(), len(x['name'])))

        # Assuming the uniqueness check is based on the first attraction's ID
        unique_events = []
        seen_ids = set()
        for event in sorted_events:
            attraction_id = event['_embedded']['attractions'][0]['id']
            if attraction_id not in seen_ids:
                unique_events.append(event)
                seen_ids.add(attraction_id)

        # Update or create concert instances
        for event in unique_events:
            Concert.objects.update_or_create(
                event_id=event['id'],
                defaults={
                    'name': event['name'],
                    'image_url': event['images'][0]['url'],
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
            )
    
        concerts = Concert.objects.all()
        concerts_json = serialize('json', concerts)
        parsed_data = json.loads(concerts_json)  # Parse the JSON string into a Python object
        return JsonResponse(parsed_data, safe=False, json_dumps_params={'indent': 4})
    else:
        # Handle errors or unsuccessful responses
        print("Failed to fetch concerts data")
        return None
    
def get_markets(request):
    markets = Market.objects.all()
    
    # Serialize the queryset
    data = [{"name": market.description, "id": market.pk} for market in markets]
    
    # Return an HttpResponse with the serialized data
    return JsonResponse(data, safe=False)