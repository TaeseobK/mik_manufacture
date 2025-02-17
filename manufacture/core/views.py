from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate
from user_profile.models import Profile
from django.http import JsonResponse
from .models import UserActivity
from django.core.files.storage import default_storage
import requests

def home(request) :
    u = request.user

    if u.is_authenticated :
        user = User.objects.using('default').get(id=int(u.pk))
        profile = Profile.objects.using('profile').get(user=int(user.pk))

    else :
        profile = ''

    return render(request, 'core/home.html', {
        'title' : 'Home',
        'profile' : profile if profile else None
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

@login_required(login_url='/login/')
def profile(request, id_user) :

    user = request.user

    profile = Profile.objects.using('profile').get(user=int(id_user))

    if request.method == 'POST' :
        metode = request.POST['metode']

        if metode == 'update-profile' :
            files = request.FILES.get('image-profile')
            user = request.user
            phone = request.POST['phone']
            company = request.POST['company']
            username = request.POST['username']
            about = request.POST['about']
            first_name = request.POST['first-name']
            last_name = request.POST['last-name']
            email = request.POST['email']
            state = request.POST['state']
            city = request.POST['city']
            zip = request.POST['zip']

            file_name = None

            if files :
                file_name = f'profile_images/{files.name}'
                file_name = default_storage.save(file_name, files)
                file_url = default_storage.url(file_name)

            new_p = Profile.objects.using('profile').get(user=user.pk)

            new_p.phone = phone
            new_p.image = file_name if file_name else 'Doesnt Exist'
            new_p.company = company
            new_p.about = about
            new_p.province = state
            new_p.city = city
            new_p.zip = zip
            new_p.save()

            up_user = User.objects.using('default').get(id=int(user.pk))

            up_user.username = username
            up_user.first_name = first_name
            up_user.last_name = last_name
            up_user.email = email
            up_user.save()

            return redirect('core:user_profile', id_user=id_user)
        
        elif metode == 'update-password' :
            old = request.POST['old-password']
            new = request.POST['new-password']
            retype = request.POST['retype-password']
            user_new = User.objects.using('default').get(id=int(id_user))

            print(old)
            print(new)
            print(user_new.password)

            if new == retype :
                if user_new.check_password(old) :
                    user_new.set_password(new)
                    user_new.save()

                    update_session_auth_hash(request, user_new)
                    messages.success(request, "Your Password Has Been Changed")
                    return redirect('core:home')
                
                else :
                    messages.error(request, "Incorrect Old Password!")
                    return redirect('core:user_profile', id_user=id_user)

            else :
                messages.error(request, "Your New Password and Confirmation Password Does Not Match")
                return redirect('core:user_profile', id_user=id_user)

    return render(request, 'core/profile.html', {
        'title' : 'User Profile',
        'profile' : profile
    })

def get_province(request) :
    url = 'https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json'
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 :
        return JsonResponse(data, safe=False)
    
    else :
        return JsonResponse({'error' : 'Failed to fetch data'}, status=500)
    
def get_cities(request, province_id) :
    url = f'https://www.emsifa.com/api-wilayah-indonesia/api/regencies/{province_id}.json'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 :
        return JsonResponse(data, safe=False)
    
    else :
        return JsonResponse({'error' : 'Failed to fetch cities'}, status=500)