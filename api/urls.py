from django.urls import path
from .views import adhd, dyslexia

urlpatterns = [
    path('adhd/', adhd.as_view(), name='adhd'),
    path('dyslexia/', dyslexia.as_view(), name='dyslexia'),
]