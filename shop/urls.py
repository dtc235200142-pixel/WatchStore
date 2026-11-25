from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('cart/', views.cart_view, name='cart'),

    path('cart/add/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),

    path('cart/remove/<int:product_id>/',
         views.remove_from_cart, name='remove_from_cart'),

    path('cart/update/<int:product_id>/',
         views.update_cart, name='update_cart'),

    path('checkout/',
         views.checkout, name='checkout'),

    path('order-success/<int:order_id>/',
         views.order_success, name='order_success'),

    path('orders/',
         views.order_history, name='orders'),
]