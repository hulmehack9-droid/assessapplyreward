from django.contrib import admin
from django.urls import path
from FrontEnd import hello_world

urlpatterns = [

    path('', hello_world),  # This maps the root URL to your view
]