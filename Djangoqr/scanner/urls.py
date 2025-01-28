from django.urls import path
from scanner.views import generate_qr,scan_qr

urlpatterns = [
  path('generate/',generate_qr,name='generate'),
  path('scan/',scan_qr,name='scan')

    
]
