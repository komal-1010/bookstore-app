# payments/views.py
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from store.models import Order
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"Order #{order.id}"},
                    'unit_amount': int(order.total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/order-confirmation/{order.id}",
            cancel_url=f"{settings.FRONTEND_URL}/payment-cancel",
        )

        Payment.objects.create(
            order=order,
            stripe_session_id=session.id,
            status='pending'
        )

        return Response({"id": session.id, "url": session.url})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["success_url"].split("/")[-1].split("?")[0]  # extract order id
        try:
            order = Order.objects.get(id=order_id)
            order.status = "placed"
            order.save()
        except Order.DoesNotExist:
            pass

        # update payment table
        Payment.objects.filter(stripe_checkout_id=session["id"]).update(status="paid")

    return HttpResponse(status=200)