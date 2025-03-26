from django.contrib.auth import get_user_model
from django.db import models
from Config.customers.models import CustomerOrder
User = get_user_model()
KUTILMOQDA, QABUL_QILINDI, BEKOR_QILINDI = ('kutilmoqda', 'qabul qilindi', 'bekor qilindi')


class DriverOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car_type = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.username}'s {self.car_name} ({self.car_number}) - {self.car_type}"


class DriverRequest(models.Model):
    driver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_requests')  # Foydalanuvchi
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)  # Faqat order ko'rinadi
    REQUEST_STATUS = (
        (KUTILMOQDA, KUTILMOQDA),
        (QABUL_QILINDI, QABUL_QILINDI),
        (BEKOR_QILINDI, BEKOR_QILINDI)
    )
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default=KUTILMOQDA)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.driver_user.username} for order {self.customer_order.id} - {self.status}"