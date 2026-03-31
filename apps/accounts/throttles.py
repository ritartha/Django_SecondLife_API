from rest_framework.throttling import AnonRateThrottle


class OTPRateThrottle(AnonRateThrottle):
    rate = '3/minute'
    scope = 'otp'