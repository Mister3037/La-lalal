from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import *
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import *
# Create your views here.
User = get_user_model()



# Telefon raqam orqali ro'yhatdan o'tadi
class CreateUser(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUPSerializer


class CheckPhoneDatabase(APIView):
    def post(self, request):
        serializer = CheckPhoneDatabaseSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone']
            if not User.objects.filter(phone=phone_number).exists():
                return Response({"exists": False})
        return Response({'exists': True})


class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user             # user ->
        code = self.request.data.get('code') # 4083

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "token": user.token()['access'],
                # "refresh": user.token()['refresh_token']
            }
        )


@staticmethod
def check_verify(user, code):   
    verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
    print(verifies)
    if not verifies.exists():
        data = {
            "message": "Tasdiqlash kodingiz xato yoki eskirgan"
        }
        raise ValidationError(data)
    else:
        verifies.update(is_confirmed=True)
        user.save()
    return True



# class ChangeUserAPIView(UpdateAPIView):
#     permission_classes = [IsAuthenticated, ]
#     serializer_class = UpdateUserSerializer
#     queryset = User.objects.all()
#     http_method_names = ['put', 'patch']

#     def get_object(self):
#         return self.request.user

#     def update(self, request, *args, **kwargs):
#         user = self.request.user
#         super(ChangeUserAPIView, self).update(request, *args, **kwargs)
#         return Response(
#             {"message": "User update successfully",
#              "username": user.username,
#              "user_image": str(user.user_image),
#              "access": user.token()['access'],
#              "refresh_token": user.token()['refresh_token']})

#     def partial_update(self, request, *args, **kwargs):
#         user = self.request.user
#         super(ChangeUserAPIView, self).update(request, *args, **kwargs)
#         return Response(
#             {"message": "User update successfully",
#              "username": user.username,
#              "user_image": str(user.user_image),
#              "access": user.token()['access'],
#              "refresh_token": user.token()['refresh_token']})


class ChangeUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # current_imei = user.imei
        # if not User.objects.filter(id=user.id, imei=current_imei).exists():
            #  return Response({"error": "IMEI raqami topilmadi!"}, status=404)
        data = {
            "username": user.username,
            "user_image": str(user.user_image),
            "access": user.token()['access'],
            "refresh_token": user.token()['refresh_token']
        }
        return Response(data)


    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UpdateHumanSerializer(user, data=request.data)  # PUT - to'liq yangilash
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "username": user.username,
                "user_image": str(user.user_image),
                "access": user.token()['access'],
                "refresh_token": user.token()['refresh_token']
            })
        return Response(serializer.errors, status=400)
    
    
    def patch(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UpdateHumanSerializer(user, data=request.data, partial=True)  # PATCH - qisman yangilash
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "username": user.username,
                "user_image": str(user.user_image),
                "access": user.token()['access'],
                "refresh_token": user.token()['refresh_token']
            })
        return Response(serializer.errors, status=400)



class FullUserInformationAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated ]
    queryset = User.objects.all()
    serializer_class = FullUserInformationSerializer

    def get_object(self):
        return self.request.user
        
    
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        user = User.objects.filter(phone=data['phone']).first()

        if not user:
            return Response({'error': 'Bunday foydalanuvchi topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
        if check_password(data['password'], user.password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'token': access_token,
                'phone': str(user.phone),
                'role': user.role
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Parolingiz xato'}, status=status.HTTP_400_BAD_REQUEST)



class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = self.request.user
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "Foydalanuvchi muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)


class LogOutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': "Muvaffaqiyatli hisobingizdan chiqdingiz!"
            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)
            


class ResetPasswordAPIView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()  # Barcha foydalanuvchilarni oladi

    def patch(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        # Foydalanuvchini telefon raqami orqali topish
        user = self.get_queryset().filter(phone=phone).first()  # queryset dan foydalanish
        if user:
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)  # Validatsiya qilish
            serializer.save()  # Parolni yangilash
            return Response({"detail": "Parol muvaffaqiyatli yangilandi."})
        else:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_400_BAD_REQUEST)
            
            
        
class SendCodeAPIView(APIView):
    def post(self, request):
        # Serializer orqali telefon raqami tekshiriladi
        serializer = SendCodeSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')

            try:
                # SMS yuboriladi
                code = serializer.send_verification_code(phone)
                return Response({'verification_code': code}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer

