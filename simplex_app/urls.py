from django.urls import path
from simplex_app import views

app_name = 'simplex_app'

urlpatterns = [
    path('', views.portada, name='portada'),             # La portada (landing page)
    path('inicio/', views.index, name='index'),          # Formulario inicial
    path('resolver/', views.solve, name='solve'),        # Ingreso de datos y resolución
    path('resultados/', views.results, name='results'),  # Redirección
]