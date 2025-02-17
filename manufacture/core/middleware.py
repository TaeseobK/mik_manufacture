import time
from .models import *
from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import *

class UserActivityMiddleware:
    """
    Middleware untuk melacak aktivitas user yang login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            username = request.user.username
            path = request.path
            method = request.method
            timestamp = now()
            ip_address = request.META.get('REMOTE_ADDR')

            UserActivity.switch_table()

            self.log_activity(user_id, username,path, method, timestamp, ip_address)

        response = self.get_response(request)
        return response

    def log_activity(self, user_id, username,path, method, timestamp, ip_address):

        if not method == 'GET' :
        
            UserActivity.objects.using('dump').create(
                user=user_id,
                username=username,
                path=path,
                method=method,
                timestamp=timestamp,
                ip_address=ip_address
            )

        else :
            pass

class AutoLogout :
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated :
            return self.get_response(request)
        
        max_idle_time = getattr(settings, 'AUTO_LOGOUT_TIME', 900)

        last_activity = request.session.get('last_activity')
        if last_activity :
            if '+' in last_activity or '-' in last_activity :
                last_activity_time = timezone.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f%z')
            else :
                last_activity_time = timezone.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
            idle_time = (timezone.now() - last_activity_time).seconds
            if idle_time > max_idle_time :
                logout(request)

        request.session['last_activity'] = str(timezone.now())

        return self.get_response(request)