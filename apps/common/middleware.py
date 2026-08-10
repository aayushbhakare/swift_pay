import time

import logging

from django.conf import settings

from django.http import JsonResponse



logger = logging.getLogger('apps.common')







class RedisRateLimiterMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response



    def __call__(self, request):

        if request.path.startswith('/api/v1/payments/'):

            client_ip = self.get_client_ip(request)

            capacity = getattr(settings, 'RATE_LIMIT_BURST_CAPACITY', 10)

            refill_rate = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 60) / 60.0



            allowed = self.check_rate_limit(client_ip, capacity, refill_rate)

            if not allowed:

                logger.warning(f"Rate limit exceeded for IP: {client_ip}")

                return JsonResponse({

                    "error": {

                        "code": "TOO_MANY_REQUESTS",

                        "message": "Rate limit exceeded. Please try again later."

                    }

                }, status=429)



        return self.get_response(request)



    def check_rate_limit(self, client_ip, capacity, refill_rate):

        try:

            import redis

            redis_client = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1)

            key = f"rate_limit:{client_ip}"

            now = time.time()

            pipe = redis_client.pipeline()

            pipe.hget(key, 'tokens')

            pipe.hget(key, 'last_refill')

            res = pipe.execute()



            tokens = float(res[0]) if res[0] is not None else capacity

            last_refill = float(res[1]) if res[1] is not None else now



            elapsed = now - last_refill

            tokens = min(capacity, tokens + elapsed * refill_rate)



            if tokens >= 1.0:

                tokens -= 1.0

                pipe = redis_client.pipeline()

                pipe.hset(key, 'tokens', tokens)

                pipe.hset(key, 'last_refill', now)

                pipe.expire(key, 120)

                pipe.execute()

                return True

            return False

        except Exception as e:

            logger.error(f"Redis rate limiter unavailable: {e}")

            

            

            

            raise e



    def get_client_ip(self, request):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:

            return x_forwarded_for.split(',')[0].strip()

        return request.META.get('REMOTE_ADDR', '127.0.0.1')

