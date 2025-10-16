# jobs/urls.py
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='list'),
    path('<int:job_id>/', views.job_detail_view, name='detail'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
]