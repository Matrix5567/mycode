import json
import urllib
import requests

from django.shortcuts import render , redirect , HttpResponse
from django.http import JsonResponse
from django.views import View
from .models import Category , Product , CustomUser , Cart , Stripe
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate , logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
import random
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import stripe
from twilio.rest import Client
from rest_framework import generics
from .serializers import Apiserializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
import ast

# Create your views here.
class Home(View):                                  # all products pagenation , search , low to high , high to low , newest first
    def get(self, request):
        x = Category.objects.all()
        y = Product.objects.all()
        search_val = request.GET.get("search")
        fltr_type = request.GET.get("filter_type")
        if search_val:
            search_name = request.GET.get('search')
            if search_name:
                y = Product.objects.filter(name__icontains=search_name)
        if fltr_type:
            if fltr_type == 'l2h':
                y = Product.objects.all().order_by("discountamount")
            elif fltr_type == 'h2l':
                y = Product.objects.all().order_by("-discountamount")

            elif fltr_type == 'nwst':
                y = Product.objects.all().order_by("-id")

        p = Paginator(y, 5)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        context = {
            'category': x,
            'page_obj': page_obj,
            'filter_type': fltr_type,
            }
        form = CustomUserCreationForm()
        context['f'] = form
        return render(request, 'firstpage.html', context)


class Items(View):                             #  specific products pagenation  , low to high , high to low , newest first
    def get(self,request):
        product = request.GET.get("product")
        fltr_type = request.GET.get("filter_type")
        search_val =  request.GET.get("search")
        if product:
            cat = Category.objects.get(name=product)
            objects = Product.objects.filter(category=cat)
            a = objects
            if fltr_type and product is not None:
                if fltr_type == 'l2h':
                    y = a.order_by("discountamount")
                    a = y
                elif fltr_type == 'h2l':
                    y = a.order_by("-discountamount")
                    a = y
                elif fltr_type == 'nwst':
                    y = a.order_by("-id")
                    a = y

        if search_val:
            product = request.GET.get("category")
            cat = Category.objects.get(name=product)
            objects = Product.objects.filter(category=cat) # all products with selected category
            a = objects.filter(name__icontains=search_val) # all products with selected category and searched value

        p = Paginator(a, 5)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)

        except:
            page_obj = p.page(1)

        context = {
                    'page_obj': page_obj,
                    'category':product,
                    'filter_type':fltr_type,
                    'search':search_val,


        }
        return render(request, 'category.html', context)


class Detail(View):
    def get(self,request):
        if request.user.is_authenticated:
            current_user = request.user
            try:
                Token.objects.get(user=current_user)
                prdct_id = request.GET.get('id')
                product = Product.objects.get(id=prdct_id)
                context = {
                    'item': product
                }
                return render(request, 'detail.html', context)
            except:
                return HttpResponse("Invalid Token")
        else:
            prdct_id = request.GET.get('id')
            product = Product.objects.get(id = prdct_id)
            context = {
                'item':product
            }
            return render(request,'detail.html',context)



class Login(View):
    def post(self, request, urllib2=None):
        email = request.POST.get('email')
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')
        try:
            #user=CustomUser.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values)
            req = urllib.request.Request(url, data)                      ## google captcha login
            response = urllib.request.urlopen(req.full_url)

            url_encoded = req.full_url+"?secret="+values['secret']+"&response="+values['response']
            response = requests.get(url_encoded)
            b=response.content
            result = json.loads(b)
            if user is not None and result['success']:
                token, created = Token.objects.get_or_create(user=user)
                print({'token': token.key})
                login(request, user)
                item = request.session['cart']
                current_user = request.user
                cart = json.loads(item)
                for key, value in cart.items():
                    current_product = Product.objects.get(id=key)
                    Cart(customuser=current_user, product=current_product, quantity=value).save()   ## switching to database when user is authenticated
                cart = json.dumps(cart)
                request.session['cart']=cart
                if request.session.get('cart'):
                    del request.session['cart']
                return JsonResponse({'status': '200'})
            else:
                return JsonResponse({'status': '500'})
        except:
            return JsonResponse({'status': '500'})


class Register(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'signupmodal.html',{'f':form})
    def post(self, request):
        l=[]
        y = CustomUser.objects.all()
        for i in y:
            l.append(i.email)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        ran = random.random()
        form = CustomUserCreationForm(request.POST)
        if not first_name:
            return HttpResponse("please enter your first name")
        elif not last_name:
            return HttpResponse("please enter your last name")
        elif not address:
            return HttpResponse("please enter your address")
        elif not email:
            return HttpResponse("please enter your email")
        elif email in l:
            return HttpResponse("email already registered")
        elif not phone:
            return HttpResponse("please enter your phone")
        elif not password1:
            return HttpResponse("please enter password")
        elif not password2:
            return HttpResponse("please confirm your password")
        elif password1!=password2:
            return HttpResponse("two password fields does not match")
        if form.is_valid():
            save_form = form.save(commit=False)
            save_form.username = ran
            save_form.save()
            return JsonResponse({'status': '200'})



def logout_request(request):
    try:
        current_user = request.user
        token=Token.objects.get(user=current_user)
        token.delete()
        print("token deleted")
        logout(request)
        return redirect("eweb:home")
    except:
        return HttpResponse("Invalid Token")


class Cartcount(View):
    def get(self,request):
        product_id = request.GET.get('product_id')
        if not 'cart' in request.session.keys():
            request.session['cart'] = '{}'

        cart_json = request.session['cart']
        cart = json.loads(cart_json)

        if product_id:
            if str(product_id) in cart.keys():
                cart[str(product_id)] += 1
            else:
                cart[str(product_id)] = 0
                cart[str(product_id)] += 1

            cart_json = json.dumps(cart)

            request.session['cart'] = cart_json


        if len(cart.keys()) > 0:
            num = len(cart.keys())
        else:
            num = ''

        if request.user.is_authenticated:
            current_user = request.user
            ids = []
            if product_id:
                ## saving while user is  authenticated
                current_product = Product.objects.get(id=product_id)
                cart_obj = Cart(customuser=current_user,product=current_product)
                for x in Cart.objects.filter(customuser=current_user):
                   ids.append(x.product.id)

                if int(product_id) not in ids:
                    cart_obj.quantity=1
                    cart_obj.save()
                else:
                    cart_obj = Cart.objects.get(product=current_product)
                    cart_obj.quantity+=1
                    cart_obj.save()
            num = Cart.objects.filter(customuser=current_user)
            return HttpResponse(len(num))
        return HttpResponse(num)


class Cartpage(View):
    def get(self,request):
        if request.user.is_authenticated:
            current_user = request.user
            try:
                Token.objects.get(user=current_user)
                current_user = Cart.objects.filter(customuser=current_user).order_by('id') ## listing poducts in cartpage when user is authenticated
                return render(request, 'cartpage.html', {'products':current_user})
            except:
                return HttpResponse("Invalid Token")
        else:
            qty=""
            product_list=[]
            quantity_list =[]
            item=request.session['cart']
            mycart = json.loads(item)
            for id in mycart.keys():
                y = Product.objects.get(id=id)
                product_list.append(y)
                qty=mycart.get(id)
                quantity_list.append(qty)
            z = zip(product_list,quantity_list)
            cart = json.dumps(mycart)
            request.session['cart'] = cart
            return render (request,'cartpage.html',{'products':z})   ## listing poducts in cartpage when user is not authenticated


def delete(request,id):
    quantity_list =[]
    product_list =[]
    if request.user.is_authenticated:
        items = Cart.objects.get(id=id)
        items.delete()
    else:
        item = request.session['cart']
        cart = json.loads(item)
        cart.pop(str(id))
        for i in cart.keys():
            product_list.append(i)
        for i in cart.values():
            quantity_list.append(i)
        cart = json.dumps(cart)
        request.session['cart'] = cart
        z = zip(product_list, quantity_list)
        return render(request, 'cartpage.html', {'products': z })
def total(request):
    if request.user.is_authenticated:
        amount=[]
        currentuser = request.user
        y=Cart.objects.filter(customuser=currentuser)
        for i in y:
            amount.append(i.product.discountamount*i.quantity)
        return HttpResponse(sum(amount))
    else:
        item_list = []
        item=request.session['cart']
        cart = json.loads(item)
        for id in cart:
            y = Product.objects.get(id=id)
            item_list.append(y.discountamount)
        cart = json.dumps(cart)
        request.session['cart']=cart
        return HttpResponse(sum(item_list))

def increment(request,id):
    if request.user.is_authenticated:
        y = Cart.objects.get(id=id)
        y.quantity+=1
        num=y.quantity
        y.save()
        return HttpResponse(num)
    else:
        item = request.session['cart']
        cart = json.loads(item)
        cart[str(id)]+=1
        num = cart[str(id)]
        cart = json.dumps(cart)
        request.session['cart']=cart
        return HttpResponse(num)
def decrement(request,id):
    if request.user.is_authenticated:
        y = Cart.objects.get(id=id)
        if y.quantity>1:
            y.quantity -= 1
            num = y.quantity
            y.save()
            return HttpResponse(num)
    else:
        item = request.session['cart']
        cart = json.loads(item)
        num=1
        if cart[str(id)] > 1:
            item = request.session['cart']
            cart = json.loads(item)
            cart[str(id)]-= 1
            num = cart[str(id)]
            cart = json.dumps(cart)
            request.session['cart']=cart
        return HttpResponse(num)

@method_decorator(login_required,name='dispatch')
class Checkout(View):
    def get(self, request):
        amount = []
        current_user = request.user
        try:
            Token.objects.get(user=current_user)
            current_user = Cart.objects.filter(customuser=current_user)
            for i in current_user:
                amount.append(i.product.discountamount*i.quantity)
                final_amt=sum(amount)
            return render(request, 'checkout.html',{'items':current_user,'final_amt':final_amt,'price':int(final_amt*100)})
        except:
            return HttpResponse("Invalid Token")

@method_decorator(login_required,name='dispatch')
class Paymentsuccess(View):
    def get(self, request):
        if request.user.is_authenticated:
            current_user = request.user
            try:
                Token.objects.get(user=current_user)
                if current_user:
                    subject = 'SUCCESSFULLY ORDERED'
                    message = 'Hi, thank you for order you will receive your product within one week.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [current_user, ]
                    send_mail(subject, message, email_from, recipient_list)
                return render(request,'paymentsuccess.html')
            except:
                return HttpResponse("Invalid token")

@method_decorator(login_required,name='dispatch')
class Paymentfailed(View):
    def get(self, request):
        return render(request,'paymentfailed.html')

@method_decorator(login_required,name='dispatch')
def stripe_payment(request):
    stripe.api_key = "sk_test_51KtR2ZSHGiVmY47gsaDRSKkeAd0EACIl9IfzOlY6TQIoSA4L62OKakUxbZMDOrDjEaLb45TozDVoloKYIWbbswMW00BLIZEOUT"
    current_user = request.user
    if request.user.is_authenticated:
        try:
            Token.objects.get(user=current_user)
            s = Stripe.objects.filter(customuser=current_user)
            if len(s)!=0:
                for i in s:
                    stripeuser=i
                    if current_user and stripeuser in s:
                        intent2 = stripe.PaymentMethod.create(
                            type="card",
                            card={
                                "number": request.POST['cardno'],
                                "exp_month": request.POST['expm'],
                                "exp_year": request.POST['expy'],
                                "cvc": request.POST['cvc'],
                            }
                        )
                        intent3 = stripe.Customer.create(
                            name=current_user,
                            email=current_user,
                            description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
                        )
                        intent = stripe.PaymentIntent.create(
                            amount=request.POST['price'],
                            currency="inr",
                            receipt_email="kevinbabuvarkey@gmail.com",
                            payment_method_types=["card"],
                            payment_method=intent2.get("id"),
                            description='testing',
                            customer=stripeuser,
                            confirm=True
                        )
                        to = '+91 8943196911'
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        response = client.messages.create(
                            body='FLIPKART , SUCCESSFULLY ORDERED',
                            to=to, from_=settings.TWILIO_PHONE_NUMBER)

                        account_sid = 'ACb3bfbe7b20c1e8a230d8826d799cbaf1'
                        auth_token = 'fcb7f95716c9ccf33a9719b12f8649d3'
                        client = Client(account_sid, auth_token)

                        message = client.messages.create(
                            from_='whatsapp:+14155238886',
                            body='FLIPKART , SUCCESSFULLY ORDERED',
                            to='whatsapp:+918943196911'
                        )
                        if current_user:
                            subject = 'FLIPKART-SUCCESSFULLY ORDERED'
                            message = 'Hi, thank you for order you will receive your product within one week.'
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = [current_user, ]
                            send_mail(subject, message, email_from, recipient_list)
                        return render(request, 'paymentsuccess.html')
            else:
                phone = request.POST['phone']
                print("+++",phone)
                intent2=stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "number": request.POST['cardno'],
                        "exp_month": request.POST['expm'],
                        "exp_year": request.POST['expy'],
                        "cvc": request.POST['cvc'],
                        }
                    )
                intent3=stripe.Customer.create(
                    name=current_user,
                    email=current_user,
                    description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
                )
                intent = stripe.PaymentIntent.create(
                    amount=request.POST['price'],
                    currency="inr",
                    receipt_email="kevinbabuvarkey@gmail.com",
                    payment_method_types=["card"],
                    payment_method=intent2.get("id"),
                    description='testing',
                    customer = intent3.get("id"),
                    confirm=True
                )
                Stripe(customerid=intent3.get("id"),customuser=current_user).save()
                to = '+91 8943196911'
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                response = client.messages.create(
                    body='FLIPKART , SUCCESSFULLY ORDERED',
                    to=to, from_=settings.TWILIO_PHONE_NUMBER)
                if current_user:
                    subject = 'FLIPKART-SUCCESSFULLY ORDERED'
                    message = 'Hi, thank you for order you will receive your product within one week.'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [current_user, ]
                    send_mail(subject, message, email_from, recipient_list)
                return render(request,'paymentsuccess.html')
        except:
            return HttpResponse("Invalid Token")


class API_objects(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = Apiserializer

class API_objects_details(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = Apiserializer



@api_view(['POST'])
def add_items(request):
    item = Apiserializer(data=request.data)
    print("item",item)                               #create
    '''if Product.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')'''
    if item.is_valid():
        item.save()
        return Response(item.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def view_items(request):
    items = Product.objects.all()
    serializer = Apiserializer(items, many=True)

    # if there is something in items else raise error            #listview
    if items:
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

























