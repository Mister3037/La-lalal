from django.urls import path
from .views import *

urlpatterns = [
    path('customer-post-order/', CustomerOrderAPIView.as_view()), # Eslatma! -> Order yaratish
    path('mening-buyurtmalarim/', MeningBuyurtmalarimAPIView.as_view()),
    path('orderga-sorov-yuborgan-driverlar-royhati/<int:pk>/', OrdergaMurojaatQilganDriverlarRoyhati.as_view()),
    path('orderni-ochirish/<int:pk>/', OrderniOchirishAPIView.as_view()),  # Eslatma! ->  Orderni o'chirish
    path('order-retrieve-update/<int:pk>/', OrderRetireveUpdateAPIView.as_view()), # Eslatma! -> Orderni o'zgartirish
    path('customer-qabul-qiladi-driverni/', CustomerDriverniTanlashOtklik.as_view()), # Eslatma! -> customer-qabul-qiladi-driverni
    path('customer-orderni-tasdiqlshi-tugatilgan/', CustomerOrderniTugatilganiniTasdiqlash.as_view()),
    path('barcha-buyurtmalar/', BarchaBuyurtmalarAPIView.as_view()), # Eslatma! -> Barcha Buyurtmalar ro'yhati
    path('mening-driverim/<int:pk>/', OrdergaMurojaatQilganAcceptDriver.as_view()),
    path('driverga-baho/<int:order_id>/', RateDriver.as_view()),
]