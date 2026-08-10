import pytest

from django.test import Client



@pytest.mark.django_db

def test_rate_limiter_allows_requests_under_threshold():

    client = Client()

    

    response = client.get('/api/v1/health/')

    assert response.status_code == 200



@pytest.mark.django_db

def test_rate_limiter_blocks_requests_exceeding_capacity(settings):

    settings.RATE_LIMIT_BURST_CAPACITY = 3

    client = Client()



    

    statuses = [client.post('/api/v1/payments/', data={}, content_type='application/json').status_code for _ in range(5)]

    

    

    assert 429 in statuses



import multiprocessing

import requests

from django.core.management import call_command

from multiprocessing import Pool



def hit_endpoint(url):

    return requests.get(url, headers={'X-Merchant-Key': 'valid_key_123'}).status_code



@pytest.mark.django_db(transaction=True)

def test_distributed_rate_limiter_cross_process(live_server, settings):

    from apps.merchants.models import Merchant

    Merchant.objects.create(name="Valid Merchant", api_key="valid_key_123")

    settings.RATE_LIMIT_BURST_CAPACITY = 20

    url = f"{live_server.url}/api/v1/payments/"



    

    with Pool(4) as pool:

        statuses = pool.map(hit_endpoint, [url] * 30)



    

    

    assert statuses.count(200) <= 20

    assert 429 in statuses

