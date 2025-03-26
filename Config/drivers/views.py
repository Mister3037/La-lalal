from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DriverRequest, QABUL_QILINDI, DriverOrders
from .serializers import *
from Config.customers.serializers import DriverCustomerOrderSerializers
from Config.customers.models import CustomerOrder, YAKUNLADI, TUGATILGAN



class HaydovchiningBuyurtmagaSorovYuborishAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = self.request.user
        model = DriverRequest.objects.filter(driver_user=user)
        serializer = DriverRequestListSerializer(model, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)
        # Bu yerda qo'shimcha get uchun ya'ni qaysi orderlarga buyurtma berganini chiqarish

    def post(self, request):
        current_user = self.request.user
        serializer = DriverRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver_user=self.request.user)
            data = {
                'success': True,
                'message': 'Muvvafaqiyatli so\'rov yuborildi!'
            }
            return Response(data, status.HTTP_201_CREATED)
        data={
            'error': serializer.errors
        }
        raise ValidationError(data)
        

class DriverniQabulQilganOrderlarRoyhati(APIView):  # Driverni Qabul Qilgan Orderlar ro'yhati
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        current_user = self.request.user
        try:
            model = DriverRequest.objects.filter(status=QABUL_QILINDI, driver_user=self.request.user)
        except DriverRequest.DoesNotExist:
            raise ValidationError('Ma\'lumot topilmadi!')

        serializer = DriverRequestListSerializer(model, many=True)
        return Response(
            data={
                'success': True,
                'data': serializer.data  # Serializerdan to'g'ridan-to'g'ri foydalanish
            }
        )


class DriverniOrdergaYuborganSoroviniOchirish(APIView):
    permission_classes = [IsAuthenticated, ]
    
    def delete(self, request, pk):
        driver = self.request.user
        try:
            order = CustomerOrder.objects.get(id=pk)
        except CustomerOrder.DoesNotExist:
            raise ValidationError("Bunday buyurtma topilmadi!", status.HTTP_400_BAD_REQUEST)
        try:
            driver_order = DriverRequest.objects.get(driver_user=driver, customer_order=order)
        except DriverRequest.DoesNotExist:
            raise ValidationError("Sizning bu buyurtmaga yuborgan so'rovingiz topilmadi!", status.HTTP_400_BAD_REQUEST)
        driver_order.delete()
        return Response(
            data={
                'success': True,
                'message': 'Buyurtmaga yuborgan so\'rovingiz muvaffaqiyatli o\'chirildi',
            }, 
            status=status.HTTP_204_NO_CONTENT
        )
        
        
class OrderFinishedAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response('Sizning buyurtmangiz yetib keldi!')

    def post(self, request):
        current_user = self.request.user
        serializer = MarkOrderFinishedSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        customer_order = serializer.validated_data['customer_order']
        customer_order.is_finished = YAKUNLADI 
        customer_order.save()
        return Response({
            "message": "Buyurtma holati yakunlandi",
            "data": {
                "order_id": customer_order.id,
                'status': customer_order.is_finished,
                "driver_id": request.user.id
            }
        }, status=status.HTTP_200_OK)
        
        

        