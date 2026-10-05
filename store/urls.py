from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'),
    path('category/<str:category_value>/', views.product_list, name='category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('login/', views.SoleMateLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/razorpay/create-order/', views.create_razorpay_order, name='razorpay_create_order'),
    path('checkout/razorpay/verify/', views.verify_razorpay_payment, name='razorpay_verify'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('orders/', views.order_history, name='order_history'),

    path('address/', views.address_view, name='address'),

    path('chat/api/', views.chat_api, name='chat_api'),
]
