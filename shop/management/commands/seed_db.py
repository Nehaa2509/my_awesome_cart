from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.models import Product


class Command(BaseCommand):
    help = 'Instantly seeds the database with core categories and starter lookbook products'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Initializing database seed sequence...'))

        # ⚡ Catalog dataset — field names matched to Product model exactly
        starter_products = [
            # --- GAMING CATEGORY ---
            {
                "product_name": "Wireless Gamepad Controller",
                "category": "Gaming",
                "subcategory": "Controllers",
                "price": 65,
                "description": "Ergonomic wireless gaming controller compatible with multi-platform setups. Feature-packed latency reduction matrix.",
                "image": "shop/images/gamepad.jpg",
            },
            {
                "product_name": "Ergonomic Gaming Chair",
                "category": "Gaming",
                "subcategory": "Furniture",
                "price": 220,
                "description": "High-back racing style gaming chair with adjustable lumbar support structural plates and premium matte upholstery.",
                "image": "shop/images/chair.jpg",
            },

            # --- ELECTRONICS CATEGORY ---
            {
                "product_name": "Studio Microphone",
                "category": "Electronics",
                "subcategory": "Audio",
                "price": 150,
                "description": "Professional USB condenser microphone for podcasting, studio recording, and zero-latency stream production.",
                "image": "shop/images/microphone.jpg",
            },
            {
                "product_name": "HD Webcam 1080p",
                "category": "Electronics",
                "subcategory": "Cameras",
                "price": 59,
                "description": "Full HD 1080p video calling webcam with integrated dual noise-canceling microphone arrays.",
                "image": "shop/images/webcam.jpg",
            },

            # --- FASHION CATEGORY ---
            {
                "product_name": "Designer Leather Jacket",
                "category": "Fashion",
                "subcategory": "Outerwear",
                "price": 250,
                "description": "Handcrafted premium leather jacket engineered for an unstructured, timeless modern streetwear silhouette profile.",
                "image": "shop/images/leather_jacket.jpg",
            },
            {
                "product_name": "Minimalist Canvas Backpack",
                "category": "Fashion",
                "subcategory": "Accessories",
                "price": 60,
                "description": "Water-resistant heavyweight canvas backpack featuring dedicated protective laptop utility sleeves.",
                "image": "shop/images/backpack.jpg",
            },
        ]

        created_count = 0

        for item in starter_products:
            product, created = Product.objects.get_or_create(
                product_name=item["product_name"],
                defaults={
                    "category": item["category"],
                    "subcategory": item["subcategory"],
                    "price": item["price"],
                    "description": item["description"],
                    "pub_date": timezone.now().date(),
                    "image": item["image"],
                    "views": 0,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Seeded: {product.product_name}'))
            else:
                self.stdout.write(self.style.NOTICE(f'  [--] Skip (already exists): {product.product_name}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nData ingestion complete! {created_count} new product(s) added.')
        )
