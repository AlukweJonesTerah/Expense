from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User  
from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.core.mail import EmailMessage
from django.conf import settings
from .email_utils import send_email
from django.contrib import auth

from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading



class EmailThread(threading.Thread):
    def __init__(self, send_email):
        self.send_email = send_email
        threading.Thread.__init__(self)

    def run(self):
        self.send_email.send_email(fail_silently=True)

class UsernameValidationView(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            
            if username is None:
                return JsonResponse({'username_error': 'Username is missing'}, status=400)
            
            if not username.isalnum():
                return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'username_error': 'Username already exists !!'}, status=409)
            
            return JsonResponse({'username_valid': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in the request'}, status=400)

class EmailValidationView(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')

            if email is None:
                return JsonResponse({'email_error': 'Email is missing'}, status=400)

            if not validate_email(email):
                return JsonResponse({'email_error': 'Email is invalid'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error': 'This email already exists !!'}, status=409)
            
            return JsonResponse({'email_valid': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in the request'}, status=400)




class RegistrationView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        
        messages.success(request,'Success')
        messages.warning(request,'warning')
        messages.info(request,'Info')
        messages.error(request,'error')

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        # keeping values
        context = {
            'fieldValues':request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Your password is too short')
                    return render(request, 'users/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active=False
                user.save()

                current_site = get_current_site(request)
                # This the email body
                body = {
                    'user':user,
                    'domain':current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),# encoding user id (uid)
                    'token':account_activation_token.make_token(user),
                }
                link = reverse('activate', kwargs={'uidb64': body['uid'], 'token': body['token']})
                activate_url = f"http://{current_site.domain}{link}"
                email_subject = "Activate your account"
                email_body = f"Hi {user.username}, Please use the link below to activate your account {activate_url}, noreply@semicolon.com"
                recipient_email = email
                # send_email(email_subject, email_body, recipient_email)

                email_thread = EmailThread(send_email(email_subject, email_body, recipient_email))
                email_thread.start()

                messages.success(request, 'Account successfully created')
                return redirect('registration')  # Redirect to the registration page or any other page you prefer

        return render(request, 'users/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            else:
                user.is_active = True
                user.save()
                messages.success(request, 'Account activated successfully')
                return redirect('login')

        except Exception as e:
            pass

        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            print(user)

            if user:
                print("user.is_active:", user.is_active)
                if user.is_active:
                    
                    auth.login(request, user)
                    messages.success(request, f'Welcome {user.username} you are now logged in')
                    return redirect('/')
                else:
                    messages.error(request, 'Account is not activated, please check your email')
                    return render(request, 'users/login.html')
            else:
                messages.error(request, 'Invalid credentials, try again')
                return render(request, 'users/login.html')
        else:
            messages.error(request, 'Please fill all fields')
            return render(request, 'users/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    
class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'users/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']
        context =  {
            'values': request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'users/reset-password.html', context)
        current_site = get_current_site(request)

        user = User.objects.filter(email=email)

        if user.exists():
            email_content = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),  # encoding user id (uid)
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }
            link = reverse('reset-new-password', kwargs={'uidb64': email_content['uid'], 'token': email_content['token']})
            reset_url = f"http://{current_site.domain}{link}"
            email_subject = "Password Reset Instructions"
            email_body = f"Hi there, Please use the link below to reset your password {reset_url}, noreply@semicolon.com"
            recipient_email = email
            # send_email(email_subject, email_body, recipient_email)

            # Create an EmailThread instance and start the thread to send the email
            email_thread = EmailThread(send_email(email_subject, email_body, recipient_email))
            email_thread.start()
 
        messages.success(request, "We have sent you an email to rest your password")
        # This the email body


        return render(request, 'users/reset-password.html')

class CompletePassword(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, "This password reset link is invalid or used request a new one")
                return render(request, 'users/reseet-password.html')
            return redirect('login')
        except Exception as e:
            messages.info(request, 'Something went wrong try again')
            return (request, 'users/set-new-password.html', context)
        return (request, 'users/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match! ')
            return (request, 'user/set-new-password.html', context)
        if len(password) < 6:
            messages.error(request, 'Password is too short ')
            return (request, 'user/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset was successful")
            return redirect('login')
        except Exception as e:
            messages.info(request, 'Something went wrong try again')
            return (request, 'user/set-new-password.html', context)