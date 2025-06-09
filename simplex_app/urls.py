from django.urls import path
from simplex_app import views

app_name = 'simplex_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('solve/', views.solve, name='solve'),
    path('results/', views.results, name='results'),
]