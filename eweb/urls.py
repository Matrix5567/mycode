from django.urls import path, include
from.views import Home , Items , Detail , Login , Register ,logout_request , Cartcount , Cartpage , delete ,increment,decrement ,total,Checkout,Paymentsuccess,Paymentfailed,API_objects,API_objects_details
from django.conf.urls.static import static
from django.conf import settings
from. import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'eweb'

urlpatterns = [
    path('', Home.as_view(),name='home'),
    path('category/', Items.as_view(),name = 'category'),
    path('detail', Detail.as_view(), name='detail'),
    path('login',Login.as_view(),name='login'),
    path('register',Register.as_view(),name='register'),
    path("logout", views.logout_request, name="logout"),
    path("cartcount",Cartcount.as_view(),name='cartcount'),
    path("cartpage",Cartpage.as_view(),name='cartpage'),
    path('delete/<int:id>/',views.delete,name='delete'),
    path('total',views.total,name='total'),
    path('increment/<int:id>/',views.increment,name='increment'),
    path('decrement/<int:id>/',views.decrement,name='decrement'),
    path1("checkout",Checkout.as_view(),name='checkout'),
    #path('create-checkout-session',views.create_checkout_session,name='create-checkout-session'),
    path('paysuc', Paymentsuccess.as_view(), name='paysuc'),
    path('payfail', Paymentfailed.as_view(), name='payfail'),
    path('stripe', views.stripe_payment, name='stripe'),
    path('basic/', views.API_objects.as_view()),
    path('basic/<int:pk>/', views.API_objects_details.as_view()),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('create/', views.add_items, name='add-items'),
    path('all/', views.view_items, name='view_items'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)

