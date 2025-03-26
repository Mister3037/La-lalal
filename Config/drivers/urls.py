from django.urls import path
from .views import *

urlpatterns = [
    path('driver-sorov-buyurtmaga/', HaydovchiningBuyurtmagaSorovYuborishAPIView.as_view()),
    path('order-isfinished/', OrderFinishedAPIView.as_view()),
    path('driver-orderga-yuborgan-sorovini-ochirish/<int:pk>/', DriverniOrdergaYuborganSoroviniOchirish.as_view()),
    path('driverni-qabul-qilgan-orderlar-royhati/', DriverniQabulQilganOrderlarRoyhati.as_view()),
]
