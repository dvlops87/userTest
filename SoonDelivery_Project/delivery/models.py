from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.

class delivery_info(models.Model):
    delivery_owner = models.ForeignKey('account.User', on_delete=CASCADE, default='',related_name='order_man' )
    delivery_man = models.ForeignKey('account.User', on_delete=CASCADE, default='', null=True)
    delivery_location  = models.CharField(max_length=40)
    ordered_time = models.DateTimeField(auto_now_add=True, blank=True)
    delivered_time = models.DateTimeField(auto_now_add=True, blank=True)
    delivery_price = models.IntegerField(default=0)
    time_required = models.IntegerField(default=0)
    stuff_price = models.IntegerField(default=0)
    delivery_list = models.TextField(default='')
    extra_order = models.TextField(default='')
    store_location = models.CharField(max_length=30, default='')
    is_delivered = models.IntegerField(default=0)
    # 0이면 배달 대기, 1이면 배달 수락, 2이면 배달 도착
    def __str__(self):
        return str(self.delivery_owner)

class chat_info(models.Model):
    order = models.ForeignKey('account.User', on_delete=CASCADE, default='',related_name='order')
    delivery = models.ForeignKey('account.User', on_delete=CASCADE, default='',related_name='delivery')