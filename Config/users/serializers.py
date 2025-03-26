# from ctypes import windll
import requests
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *



class SignUPSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'phone', 'role', 'password']

    def create(self, validated_data):
        user = super(SignUPSerializer, self).create(validated_data)
        user.save()  # Foydalanuvchini saqlash
        return user

    def to_representation(self, instance):
        result = {
            "username": instance.username,
            "role": instance.role,
            "token": instance.token()["access"],
            'refresh': instance.token()['refresh_token']
        }
        return result
        
        

class CheckPhoneDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']
        


class FullUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'password', 'user_image']


class DriverRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'username', 'role']
    
    # def to_representation(self, instance):
    #     result = {
    #         "username": instance.username,
    #         "phone": str(instance.phone),  # phone ni ham qo'shgan holda
    #     }
    #     return result


class UpdateHumanSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'user_image'] #'phone', 'password',

    def to_representation(self, instance):
        data = super(UpdateHumanSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data

    def update(self, instance, validated_data):
        # Faylni yangilash uchun user_image ni to'g'ri o'zgartirish
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        user_image = validated_data.get('user_image', None)
        if user_image:
            instance.user_image = user_image  # Yangi rasmni saqlash
        instance.save()
        return instance



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    


class ResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ('phone', 'new_password')

    def update(self, instance, validated_data):
        # Yangi parolni o'rnatish
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)


    def send_verification_code(self, phone):
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])

        url = "http://notify.eskiz.uz/api/auth/login"

        payload = {'email': 'imronhoja336@mail.ru',
                   'password': 'ombeUIUC8szPawGi3TXgCjDXDD0uAIx2AmwLlX9M'}
        files = [

        ]
        headers = {
            # 'Authorization': f"{Bearer}"
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        token1 = response.json()["data"]["token"]

        url = "http://notify.eskiz.uz/api/message/sms/send"

        payload = {'mobile_phone': str(phone),
                   'message': f"Envoy ilovasiga ro‘yxatdan o‘tish uchun tasdiqlash kodi: {code}",
                   'from': '4546',
                   'callback_url': 'http://0000.uz/test.php'}
        files = [

        ]

        headers = {
            'Authorization': f"Bearer {token1}"
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(code)
        return code



class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data



