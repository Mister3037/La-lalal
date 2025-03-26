from rest_framework import serializers
from .models import *
from Config.users.serializers import FullUserInformationSerializer
from Config.drivers.models import DriverRequest, QABUL_QILINDI
from django.contrib.auth import get_user_model
User = get_user_model()


class UserInformation(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']
        
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"



class CustomerOrderSerializer(serializers.ModelSerializer):
    # customer_user = UserInformation(read_only=True)
    address = AddressSerializer(many=True)
    class Meta:
        model = CustomerOrder
        fields = ("id", "address", "city", "distance", "car_type", "car_count", 'height', 'length', 'load_type',
                  'weight', 'width', 'load_time', 'price', 'order_status', 'is_finished', 'comment')
                  
    
    def create(self, validated_data):
        addresses_data = validated_data.pop('address')
        order = CustomerOrder.objects.create(**validated_data)
        for address_data in addresses_data:
            Address.objects.create(order=order, **address_data)
        return order
                  


class CustomerOrderListSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = CustomerOrder
        fields = ("id", "car_type", "car_count", 'height', 'length', 'load_type',
                  'weight', 'width', 'load_time', 'price', 'order_status', 'is_finished', 'address', 'distance', 'city', 'comment')
                  

class DriverCustomerOrderSerializers(serializers.ModelSerializer):
    customer_user = UserInformation(source='user', read_only=True)
    customer_user_phone = serializers.CharField(source='user.phone', read_only=True)
    address = AddressSerializer(many=True)
    class Meta:
        model = CustomerOrder
        fields = ("id", "car_type", "car_count", 'height', 'length', 'load_type',
                  'weight', 'width', 'load_time', 'price', 'distance', 'city', 'address','customer_user', 'order_status', 'is_finished', "customer_user_phone")



# BUYURTMACHI SO'ROV YUBORGAN ODAMNI KO'RSATADI.
class AcceptDriverRequestSerializer(serializers.Serializer):
    driver_user = serializers.IntegerField()
    customer_order = serializers.IntegerField()

    def validate(self, data):
        driver_id = data.get('driver_user')
        customer_order_id = data.get('customer_order')  # to'g'ri maydon nomi

        # Driverni tekshirish
        try:
            driver = User.objects.get(id=driver_id, role='Driver')
        except User.DoesNotExist:
            raise serializers.ValidationError({"driver_user": "Haydovchi topilmadi"})

        # Customer orderni tekshirish
        try:
            customer_order = CustomerOrder.objects.get(id=customer_order_id, user=self.context['request'].user)
        except CustomerOrder.DoesNotExist:
            raise serializers.ValidationError({"customer_order": "Customer order not found or unauthorized."})

        # Driver requestni tekshirish
        driver_request = DriverRequest.objects.filter(driver_user=driver, customer_order=customer_order).first()
        if not driver_request:
            raise serializers.ValidationError("Driver request not found for this driver and order.")
        data['driver_request'] = driver_request
        data['customer_order'] = customer_order

        return data

    def create(self, validated_data):
        driver_request = validated_data['driver_request']
        customer_order = validated_data['customer_order']
        driver_request.status = QABUL_QILINDI
        driver_request.save()

        # driver_user ni to'g'ri oling
        customer_order.driver = driver_request.driver_user  # driver_user o'rniga driver_user ishlating
        customer_order.order_status = OLINGAN
        customer_order.save()
        return driver_request
        
        
class RatingDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingDriver
        fields = ['rate', 'comment', 'driver_user']







