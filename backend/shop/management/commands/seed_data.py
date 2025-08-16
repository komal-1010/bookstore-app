from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product, Cart, CartItem, Order, OrderItem
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with dummy book data"

    def handle(self, *args, **kwargs):
        self.stdout.write("📚 Seeding data with Books only...")

        # Create Admin User
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS("✅ Admin created: admin@example.com / admin123"))

        # Create Customer User
        if not User.objects.filter(email="user@example.com").exists():
            User.objects.create_user(
                email="user@example.com",
                password="user123",
                first_name="John",
                last_name="Reader"
            )
            self.stdout.write(self.style.SUCCESS("✅ Customer created: user@example.com / user123"))

        # Create Book Category
        category, _ = Category.objects.get_or_create(name="Books")

        # Create Book Products
        book_titles = [
            "The Great Gatsby",
            "To Kill a Mockingbird",
            "1984",
            "Pride and Prejudice",
            "Moby-Dick",
            "The Catcher in the Rye",
            "The Hobbit",
            "Harry Potter and the Sorcerer's Stone",
            "The Lord of the Rings",
            "Crime and Punishment"
        ]

        for title in book_titles:
            Product.objects.get_or_create(
                name=title,
                description=f"{title} - A must-read classic novel.",
                price=random.randint(200, 800),
                category=category,
                owner=User.objects.filter(is_admin=True).first()
            )

        self.stdout.write(self.style.SUCCESS("✅ 10 Book products created"))

        # Create Cart for Customer with 2 Books
        user = User.objects.filter(email="user@example.com").first()
        cart, _ = Cart.objects.get_or_create(user=user)

        sample_books = Product.objects.all()[:2]
        for book in sample_books:
            CartItem.objects.get_or_create(
                cart=cart,
                product=book,
                quantity=1
            )

        self.stdout.write(self.style.SUCCESS("✅ Sample cart created with 2 books"))

        # Create Sample Order for Customer
        order = Order.objects.create(
            user=user,
            shipping_address="123 Library Street, Pune",
            total_price=sum([b.price for b in sample_books]),
            status="pending"
        )

        for b in sample_books:
            OrderItem.objects.create(order=order, product=b, quantity=1, price=b.price)

        self.stdout.write(self.style.SUCCESS("✅ Sample order created"))
        self.stdout.write(self.style.SUCCESS("🎉 Book seeding completed"))
