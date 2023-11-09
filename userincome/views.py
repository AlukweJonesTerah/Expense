import datetime

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from userpreferences.models import UserPreference
from .models import Source, UserIncome
import json


def search_income(request):
    if request.method == 'POST':
        search_str = json.load(request.body).get('searchText', '')
        income = UserIncome.objects.filter(amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str,
            owner=request.user) | UserIncome.objects.filter(category__icontains=search_str, owner=request.user)
        data = income.values() # values returns all values
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/users/login')
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'sources': sources,
        'income': income,
        'page_obj': page_obj,
        'currency':currency
    }
    return render(request, 'userincome/index.html', context)


def add_income(request):
    source = Source.objects.all()
    context = {
        'sources': source,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'userincome/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/add_income.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        source = request.POST.get('source')

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'userincome/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                               source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('userincome')


@login_required(login_url='/users/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'userincome/edit-income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/edit-income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        sources = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'userincome/edit-income.html', context)

        income.owner = request.user
        income.amount = amount
        income.date = date
        income.source = sources
        income.description = description

        income.save()
        messages.success(request, 'Income updated  successfully')

        return redirect('userincome')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Expense removed')
    return redirect('userincome')

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    income = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, income)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = income.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in income:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'userincome/stats.html')
