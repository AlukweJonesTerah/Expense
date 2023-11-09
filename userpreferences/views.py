from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
import os
import json
from django.conf import settings

from .models import *
# Create your views here.

def index(request):

    currency_data = []
    
    file_path=os.path.join(settings.BASE_DIR, 'currencies.json') #accessing file in the parent directory

    with open(file_path, 'r') as json_file:

        data = json.load(json_file) # Reading the file

        for k,v in data.items():
            currency_data.append({'name':k,'value':v})
    
    exists = UserPreference.objects.filter(user=request.user).exists() # check if a user has a preference
    user_preferences = None
    
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
    
    if request.POST == 'GET':
        
        context = {
            'currencies':currency_data,
            'user_preferences':user_preferences,
        }
        
        return render(request, 'userpreferences/index.html', context)
        
    else:
        
        currency = request.POST.get('currency', False)
        if exists:
            user_preferences.currency=currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
            
        messages.success(request, 'Changes saved')
        context = {
            'currencies':currency_data,
            'user_preferences':user_preferences,
        }
        
        return render(request, 'userpreferences/index.html', context)
        

    
    # Python debugger 
    # import pdb
    # pdb.set_trace()
    