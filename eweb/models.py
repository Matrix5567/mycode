from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Product(models.Model):
    image = models.ImageField(upload_to='static/image', null=True, blank=True)
    name = models.CharField(max_length=150,null=True)
    description = models.CharField(max_length=500,null=True)
    discountamount = models.IntegerField(default=1)
    actualamount = models.CharField(max_length=100,null=True)
    off = models.CharField(max_length=100,null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    #username = None
    user = None
    email = models.CharField(max_length=50,unique=True)
    phone = models.CharField(max_length=50,blank=True,null=True)
    address = models.CharField(max_length=50,blank=True,null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

class Cart(models.Model):
    date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField()
    customuser = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)



class Stripe(models.Model):
    customerid = models.CharField(max_length=60,blank=True,null=True)
    customuser = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.customerid
