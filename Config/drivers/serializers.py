from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *
from Config.users.serializers import *
from Config.customers.models import TUGATILGAN, YAKUNLADI
from Config.customers.serializers import *
from Config.users.serializers import FullUserInformationSerializer
from rest_framework.generics import get_object_or_404
from rest_framework import status

class DriverRequestSerializer(serializers.ModelSerializer):
    customer_order = serializers.PrimaryKeyRelatedField(queryset=CustomerOrder.objects.all())
    # customer_order = CustomerOrderSerializer()
    class Meta:
        model = DriverRequest
        fields = ['customer_order', 'driver_user']
        extra_kwargs = {
            'driver_user': {'read_only': True}
        }


class DriverRequestListSerializer(serializers.ModelSerializer):
    # customer_order = DriverCustomerOrderSerializers()
    driver_user = FullUserInformationSerializer()
    customer_order = CustomerOrderListSerializer()
    class Meta:
        model = DriverRequest
        fields = ['customer_order', 'driver_user', 'status']


class AcceptDriverRequestSerializer(serializers.Serializer):
    driver_id = serializers.IntegerField()
    order_id = serializers.IntegerField()

    def validate(self, attrs):
        driver_id = attrs.get('driver_id')
        order_id = attrs.get('order_id')
        try:
            driver = User.objects.get(id=driver_id, role='Driver')
        except User.DoesNotExist:
            raise serializers.ValidationError({"driver_id": "Driver not found."})
        try:
            customer_order = CustomerOrder.objects.get(id=order_id, user=self.context['request'].user)
        except CustomerOrder.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Customer order not found or unauthorized."})
        try:
            driver_request = DriverRequest.objects.get(user=driver, customer_order=customer_order)
        except DriverRequest.DoesNotExist:
            raise serializers.ValidationError("Driver request not found for this driver and order.")
        attrs['driver_request'] = driver_request
        attrs['customer_order'] = customer_order
        return attrs

    def create(self, validated_data):
        driver_request = validated_data['driver_request']
        customer_order = validated_data['customer_order']
        DriverRequest.objects.filter(customer_order=customer_order, status='kutilmoqda', driver_user=driver_request.driver_user).exclude(id=driver_request.id).delete()
        driver_request.status = 'qabul qilindi'
        driver_request.save()
        customer_order.driver = driver_request.user
        customer_order.order_status = TUGATILGAN
        customer_order.save()
        return driver_request


class CancelDriverRequestSerializer(serializers.Serializer):
    driver_request_id = serializers.IntegerField()

    def validate_driver_request_id(self, value):
        if not DriverRequest.objects.filter(id=value).exists():
            raise serializers.ValidationError("Driver request not found.")
        return value

    def save(self, **kwargs):
        driver_request_id = self.validated_data['driver_request_id']
        driver_request = DriverRequest.objects.get(id=driver_request_id)
        driver_request.status = 'bekor qilindi'
        driver_request.save()
        return driver_request


class MarkOrderFinishedSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate(self, data):
        order_id = data.get('order_id')

        # Buyurtma olish
        customer_order = get_object_or_404(CustomerOrder, id=order_id)

        # Haydovchini olish (request user)
        driver = self.context['request'].user

        # DriverRequest ni tekshirish
        driver_request = DriverRequest.objects.filter(driver_user=driver, customer_order=customer_order).first()

        if not driver_request:
            raise serializers.ValidationError("Haydovchi bu buyurtma uchun ruxsatga ega emas.")

        # Statusni tekshirish
        if driver_request.status != QABUL_QILINDI:
            raise serializers.ValidationError("Haydovchi buyurtmani qabul qilmagan.")

        data['customer_order'] = customer_order
        data['driver_request'] = driver_request

        return data