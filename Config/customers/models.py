from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# NAQD_PUL, UZ_CARD, HUMO_CARD = ('naqd_pul', 'uz_card', 'humo_card')
FAOL, TUGATILGAN, OLINGAN = ('faol', 'tugatilgan', 'olingan')
YOLDA, YAKUNLADI = ("yo'lda", 'yakunladi')
User = get_user_model()


# TENTLI_YUK_MASHINASI, REFRIJERATOR, MEGA_FURA, YARIM_TIRKAMA, SHALANDA, LOMOVOZ, Pritsep_bortli = (0, 1,
#                                                                                                               2,
#                                                                                                               3,
#                                                                                                               4,
#                                                                                                               5,
#                                                                                                               6
#                                                                                                               )

one,two,sri,fo,fayv,six,seven,eych,nayn,ten,eleven,tvelw,onuch,ontort=(1,2,3,4,5,6,7,8,9,10,11,12,13,14)


class Address(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.address                                                                                                            



class CustomerOrder(models.Model):
    ORDER_STATUS = (
        (FAOL, FAOL),
        (OLINGAN, OLINGAN),
        (TUGATILGAN, TUGATILGAN)
    )
    # CARS = (
    #     (TENTLI_YUK_MASHINASI, TENTLI_YUK_MASHINASI),
    #     (REFRIJERATOR, REFRIJERATOR),
    #     (MEGA_FURA, MEGA_FURA),
    #     (YARIM_TIRKAMA, YARIM_TIRKAMA),
    #     (SHALANDA, SHALANDA),
    #     (LOMOVOZ, LOMOVOZ),
    #     (Pritsep_bortli, Pritsep_bortli)
    # )

    IS_FINISHED_STATUS = (
        (YOLDA, YOLDA),
        (YAKUNLADI, YAKUNLADI)
    )
    
    City_Index = (
        (one, one),
        (two, two),
        (sri, sri),
        (fo, fo),
        (fayv, fayv),
        (six, six),
        (seven, seven),
        (eych, eych),
        (nayn, nayn),
        (ten, ten),
        (eleven, eleven),
        (tvelw, tvelw),
        (onuch, onuch),
        (ontort, ontort),
        )

    car_type = models.IntegerField()
    car_count = models.IntegerField(default=1)
    height = models.CharField(max_length=30, null=True, blank=True)
    length = models.CharField(max_length=30, null=True, blank=True)
    address = models.ManyToManyField(Address)
    distance = models.CharField(max_length=50)
    load_type = models.CharField(max_length=100, default=True)
    weight = models.CharField(max_length=30, null=True, blank=True)
    width = models.CharField(max_length=30, null=True, blank=True)
    load_time = models.CharField(max_length=100)
    comment = models.CharField(max_length=500, null=True, blank=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS, default=FAOL)
    is_finished = models.CharField(max_length=50, choices=IS_FINISHED_STATUS, default=YOLDA)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    price = models.CharField(max_length=100)
    city_index = models.IntegerField(choices=City_Index)
    views = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Order by {self.user.username} to {str(self.address)}"


class RatingDriver(models.Model):
    rate = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    driver_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='rating_count')
    customer = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{str(self.driver_user)}"
