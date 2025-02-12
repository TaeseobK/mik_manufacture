from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from user_profile.models import Profile
from django.template import RequestContext
from django.conf import settings
from .models import UserActivity

def home(request) :
    return render(request, 'core/home.html', {
        'title' : 'Home'
    })

def register(request) :
    if request.method == 'POST' :
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        company = request.POST['company']

        if password == repeat_password :
            if User.objects.filter(email=email).exists() :
                messages.error(request, "This email has already taken!")
                return redirect('core:register')
            elif User.objects.filter(username=username).exists() :
                messages.error(request, "This username already taken!")
                return redirect('core:register')
            else :
                new_user = User.objects.create_user(
                    first_name = first_name,
                    last_name = last_name,
                    username = username,
                    email = email,
                    password = password
                )
                new_user.save()

                profile = Profile.objects.using('profile').create(
                    user=new_user.pk,
                    company=company,
                    phone=phone
                )
                profile.save(using='profile')

                user_credentials = auth.authenticate(username = username, password = password)
                if user_credentials is not None :
                    auth.login(request, user_credentials)

                    messages.success(request, f"Account created successfully, Welcome {username}...")
                    return redirect('core:home')
                else :
                    messages.error(request, "Authentication failed. Please try register.")
                    return redirect('core:register')
            
        else :
            messages.error(request, "Password doesn't match!")
            return redirect('core:register')
        
    return render(request, 'core/register.html', {
        'title' : 'Register'
    })

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Autentikasi user menggunakan username dan password
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # Perbaiki cara login, harus menyertakan request dan user
            auth.login(request, user)
            messages.success(request, f"Login successful. Welcome back {username}...")
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)
        
        else:
            messages.error(request, "Invalid login credentials. Please check your username or password.")
            return redirect('core:login')

    return render(request, 'core/login.html', {
        'title': 'Login'
    })

def logout(request) :
    auth.logout(request)
    messages.success(request, "Logout successfully. Have a great day...")
    return redirect('core:home')

def custom_view_404(request, exception) :
    return render(request, 'core/404.html', {
        'title' : '404 Page Not Found'
    }, status=404)

def log_activity(self, user, path, method, timestamp, ip_address) :
    UserActivity.objects.using('dump').create(
        user=user,
        path=path,
        method=method,
        timestamp=timestamp,
        ip_address=ip_address
    ).save()