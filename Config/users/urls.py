from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('refresh/', LoginRefreshView.as_view()),
    path('logout/', LogOutAPIView.as_view()),
    path('full-information-user/', FullUserInformationAPIView.as_view()),
    path('signup/', CreateUser.as_view()),
    path('code-verify/', VerifyAPIView.as_view()),
    path('change-user/', ChangeUserAPIView.as_view()),
    path('delete/<int:user_id>/', DeleteAccountAPIView.as_view()),
    path('reset-password/', ResetPasswordAPIView.as_view()),
    path('check-phone/', CheckPhoneDatabase.as_view()),
    path('send-sms/', SendCodeAPIView.as_view()),
]