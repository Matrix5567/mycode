from django.contrib import admin
from.models import Product , Category , CustomUser , Cart , Stripe

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(Stripe)
