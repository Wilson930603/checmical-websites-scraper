from rotating_proxies.policy import BanDetectionPolicy

class BanPolicy(BanDetectionPolicy):
    def response_is_ban(self, request, response):
        ban = super(BanPolicy, self).response_is_ban(request, response)

        if response.status == 404 or response.status == 500:
            return False
        else:
            return ban