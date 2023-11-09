
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="expense"),
    path('add-expense/', views.add_expense, name="add-expense"),
    path('edit-expense/<int:id>/', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>/', views.delete_expense, name="expense-delete"),
    path('search-expenses/', csrf_exempt(views.search_expenses), name="search_expenses"),
    path('expense_category_summary/', views.expense_category_summary, name="expense_category_summary"),
    path('stats/', views.stats_view, name="stats"),
    path('export-CSV/', views.export_csv, name="export-CSV"),
    path('export-excel/', views.export_csv, name="export-excel"),
    path('export-pdf/', views.export_pdf, name="export-pdf"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)