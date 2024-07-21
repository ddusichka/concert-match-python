import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Concert, Market

class ConcertTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        # Set up data for the tests
        self.client = Client()
        self.market = Market.objects.create(description="Test Market", market_id=1000)
        self.concert = Concert.objects.create(
            name="Sample Concert",
            event_id="EVT123",
            url="http://example.com",
            image_url="http://example.com/image.jpg",
            attraction_id="ATTR123",
            attraction_name="Sample Attraction",
            local_date=timezone.now().date(),
            local_time=timezone.now().time(),
            genre="Rock",
            subgenre="Alternative Rock",
            min_price=50.00,
            max_price=150.00,
            market=self.market,
            venue="Sample Venue",
            city="Sample City",
            state="Sample State"
        )
        self.list_url = reverse('get_concerts')
        self.fetch_url = reverse('fetch_concerts')
        self.markets_url = reverse('get_markets')

    def test_concert_list(self):
        # Test getting fetched concerts
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.concert.name, response.content.decode())

    def test_fetch_concerts(self):
        # Test fetching concerts from Ticketmaster
        response = self.client.post(self.fetch_url, data=json.dumps({"marketId": 11, "size": 5}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        data = json.loads(response.content.decode())
        all_have_marketId_11 = True
        for item in data:
            if '_embedded' in item and isinstance(item['_embedded'], dict) and 'venues' in item['_embedded'] and isinstance(item['_embedded']['venues'], list):
                for venue in item["_embedded"]["venues"]:
                    if not any(market["id"] == "11" for market in venue.get("markets", [])):
                        all_have_marketId_11 = False
                        break
    
        self.assertTrue(all_have_marketId_11, "Not all venues contain marketId 11")

    def test_get_markets(self):
        # Test getting markets
        response = self.client.get(self.markets_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.market.description, response.content.decode())