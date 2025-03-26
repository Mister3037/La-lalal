from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotFound
from django.template.context_processors import request
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from Config.drivers.serializers import *
from .serializers import *
from rest_framework import status
from rest_framework.exceptions import ValidationError


User = get_user_model()
from .serializers import *
from .models import CustomerOrder



class CustomerOrderAPIView(APIView):
    def post(self, request):
        addresses_data = request.data.get('addresses', [])
        distance = request.data.get('distance')
        car_type = request.data.get('car_type')
        car_count = request.data.get('car_count')
        height = request.data.get('height')
        length = request.data.get('length')
        load_type = request.data.get('load_type')
        weight = request.data.get('weight')
        width = request.data.get('width')
        load_time = request.data.get('load_time')
        price = request.data.get('price')
        order_status = request.data.get('order_status')
        comment = request.data.get('comment')
        city = request.data.get('city')

       
        order = CustomerOrder.objects.create(
            distance=distance,
            car_type=car_type,
            car_count=car_count,
            height=height,
            length=length,
            load_type=load_type,
            weight=weight,
            width=width,
            load_time=load_time,
            price=price,
            order_status=order_status,
            comment=comment,
            city=city,
            user=self.request.user
        )
        order.save()

        
        for address_data in addresses_data:
            address = Address(
                address=address_data['address'],
                latitude=address_data.get('latitude'),  
                longitude=address_data.get('longitude')  
            )
            address.save()
            order.address.add(address)  

        return Response({'message': 'Order created successfully!', "phone": str(self.request.user)}, status=status.HTTP_201_CREATED)



class OrderRetireveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        try:
            obj = CustomerOrder.objects.get(pk=self.kwargs["pk"], user=self.request.user)
        except CustomerOrder.DoesNotExist:
            raise ValidationError({"error": "Buyurtma topilmadi!"})
        return obj
        

class OrderniOchirishAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    
    def delete(self, request, pk):
        user = self.request.user
        try:
            customer_order = CustomerOrder.objects.get(id=pk)
        except CustomerOrder.DoesNotExist:
            raise ValidationError("Bunday order topilmadi!", status.HTTP_400_BAD_REQUEST)
        if customer_order.user.id != self.request.user.id:
            raise ValidationError("Siz buyurtma egasi emassiz!", status.HTTP_400_BAD_REQUEST)
        customer_order.delete()
        return Response(
            data={
                'success':True,
                'message': 'Buyurtma muvaffaqiyatli o\'chirildi!',
            }, status = status.HTTP_204_NO_CONTENT
        )


class MeningBuyurtmalarimAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        current_user = self.request.user
        if current_user.is_anonymous:
            raise PermissionDenied("Siz autentifikatsiya qilinmagan foydalanuvchisiz.")  # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        customer_orders = CustomerOrder.objects.filter(user=current_user).order_by("-id") # Foydalanuvchining buyurtmalarini olish
        if not customer_orders.exists():
            raise NotFound("Sizning buyurtmangiz yo'q") # Agar buyurtmalar topilmasa, 404 xato qaytadi
        serializer = CustomerOrderListSerializer(customer_orders, many=True) # Serializer orqali ma'lumotlarni tayyorlash
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerDriverniTanlashOtklik(APIView):  
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AcceptDriverRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            driver_request = serializer.save()  
            # Boshqa haydovchi so'rovlarini o'chirish
            return Response({
                "message": "Driver request accepted successfully.",
                "driver_request": DriverRequestListSerializer(driver_request).data
            }, status=200)
        return Response(serializer.errors, status=400)


class CustomerOrderniTugatilganiniTasdiqlash(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        current_user = self.request.user
        customer_order_id = request.data.get('customer_order')
        try:
            customer_order = CustomerOrder.objects.get(id=customer_order_id, user=current_user)
        except CustomerOrder.DoesNotExist:
            raise NotFound("Buyurtma topilmadi yoki sizga tegishli emas!")
        customer_order.order_status = TUGATILGAN
        customer_order.save()
        return Response(
            data={
                'success':True,
                'message': 'Buyurtma muvaffaqiyatli tasdiqlandi!'
            }, status=status.HTTP_200_OK
        )


class BarchaBuyurtmalarAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        current_user = self.request.user
        orders = CustomerOrder.objects.all()[::-1]
        serializer = CustomerOrderListSerializer(orders, many=True)
        return Response(serializer.data)
        


class OrdergaMurojaatQilganDriverlarRoyhati(RetrieveAPIView):
    queryset = DriverRequest.objects.all()
    serializer_class = DriverRequestSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = self.request.user
        pk = self.kwargs.get('pk')  
        try:
            customer_order = CustomerOrder.objects.get(pk=pk) 
        except CustomerOrder.DoesNotExist:
            return Response({'detail': 'Customer order not found.'}, status=404)
        driver_requests = DriverRequest.objects.filter(customer_order=customer_order)
        driver_request_data = [
            {                                           
                "driver_user": {
                    "id": driver_request.driver_user.id,
                    "phone": str(driver_request.driver_user.phone),
                    "username": driver_request.driver_user.username,
                }
            }
            for driver_request in driver_requests
        ]
        order_data = CustomerOrderSerializer(customer_order).data
        response_data = {
            'customer_order': order_data,
            'driver_requests': driver_request_data
            }
        return Response(response_data)
        
        

class OrdergaMurojaatQilganAcceptDriver(RetrieveAPIView):
    queryset = DriverRequest.objects.all()
    serializer_class = DriverRequestSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk') 
        try:
            customer_order = CustomerOrder.objects.get(pk=pk) 
        except CustomerOrder.DoesNotExist:
            return Response({'detail': 'Customer order not found.'}, status=404)
        driver_requests = DriverRequest.objects.filter(customer_order=customer_order, status=QABUL_QILINDI) 
        driver_request_data = [
            {                                            
                "driver_user": {
                    "id": driver_request.driver_user.id,
                    "phone": str(driver_request.driver_user.phone),
                    "username": driver_request.driver_user.username,
                }
            }
            for driver_request in driver_requests
        ]
        order_data = CustomerOrderSerializer(customer_order).data
        response_data = {
            'customer_order': order_data,
            'driver_requests': driver_request_data  # Haydovchilar ro'yatini bitta listda qaytaramiz
        }
        return Response(response_data)
        
        
        
class RateDriver(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            customer_order = CustomerOrder.objects.get(id=order_id, user=request.user)
        except CustomerOrder.DoesNotExist:
            return Response({'detail': 'Order not found or you do not have permission.'}, status=status.HTTP_404_NOT_FOUND)

        driver_id = request.data.get('driver_user')

        try:
            driver_request = DriverRequest.objects.get(customer_order=customer_order, driver_user__id=driver_id)
        except DriverRequest.DoesNotExist:
            return Response({'detail': 'No driver request found for this order and driver.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RatingDriverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver_user=driver_request.driver_user, customer=customer_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)