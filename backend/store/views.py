from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Product, Category, Cart, Order, CartItem, OrderItem
from .serializers import ProductSerializer, CategorySerializer, CartSerializer, OrderSerializer
from user.permissions import IsAdminOrReadOnly
from rest_framework import status


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')

        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=404)

        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def list(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)

    def create(self, request):
        """User creates an order from their cart."""
        shipping_address = request.data.get('shipping_address')
        if not shipping_address:
            return Response({'error': 'Shipping address is required'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = cart.total_price
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=total_price,
            status="pending"  # payment not yet done
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the cart
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        Admin or payment success can update order status.
        Example: {"status": "placed"}
        """
        order = self.get_object()

        if not request.user.is_admin:
            # Only allow user to update status if payment success callback
            if request.data.get("status") != "placed":
                return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status not in ["pending", "placed", "shipped", "delivered", "cancelled"]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)