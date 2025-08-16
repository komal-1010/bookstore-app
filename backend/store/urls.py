from .views import ProductViewSet, CategoryViewSet, CartViewSet, OrderViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)

cart_list = CartViewSet.as_view({'get': 'list'})
cart_add = CartViewSet.as_view({'post': 'add_item'})
cart_remove = CartViewSet.as_view({'post': 'remove_item'})

order_list = OrderViewSet.as_view({'get': 'list', 'post': 'create'})

urlpatterns = [
    path('cart/', cart_list, name='cart-list'),
    path('cart/add/', cart_add, name='cart-add'),
    path('cart/remove/', cart_remove, name='cart-remove'),
    path('orders/', order_list, name='order-list'),
]

urlpatterns += router.urls
