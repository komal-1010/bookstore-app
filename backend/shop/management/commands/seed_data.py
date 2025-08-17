from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product, Cart, CartItem, Order, OrderItem
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with dummy book data in multiple categories"

    def handle(self, *args, **kwargs):
        self.stdout.write("📚 Seeding data with categorized Books...")

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

        # Define categories and associated book titles
        categories_books = {
            "Fiction": [
                "The Great Gatsby", "To Kill a Mockingbird", "1984"
            ],
            "Fantasy": [
                "Harry Potter and the Sorcerer's Stone", "The Hobbit", "The Lord of the Rings"
            ],
            "Classics": [
                "Pride and Prejudice", "Moby-Dick", "The Catcher in the Rye"
            ],
            "Mystery": [
                "Crime and Punishment"
            ],
            "Science": [
                "A Brief History of Time", "The Selfish Gene"
            ],
            "History": [
                "Sapiens: A Brief History of Humankind", "Guns, Germs, and Steel"
            ]
        }

        admin_user = User.objects.filter(is_admin=True).first()

        # Create categories and add products
        for cat_name, titles in categories_books.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for title in titles:
                Product.objects.get_or_create(
                    name=title,
                    description=f"{title} - A must-read book in {cat_name}.",
                    price=random.randint(200, 800),  # Price in ₹
                    category=category,
                    owner=admin_user
                )

        self.stdout.write(self.style.SUCCESS("✅ Book products created in multiple categories"))

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
        self.stdout.write(self.style.SUCCESS("🎉 Book seeding with categories completed"))
