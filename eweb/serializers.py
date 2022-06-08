from rest_framework import serializers
from.models import Product

class Apiserializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('image', 'name', 'description', 'discountamount','actualamount','off','category')