from django.shortcuts import render
from django.contrib.auth import logout
from django.urls import reverse

class BlockUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                if request.user.userprofile.is_blocked:
                    if request.path != reverse('blocked'):
                        return render(request, 'blocked.html', status=403)
            except Exception:
                pass
        
        response = self.get_response(request)
        return response
