from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Instantly seeds the database with core categories, starter products, and blog posts'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Initializing database seed sequence...'))

        # ⚡ Product catalog dataset
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

        # 📰 Blog post dataset
        starter_posts = [
            {
                "title": "Welcome to Our Awesome Blog!",
                "chead": "This is the subheading of the first post",
                "category": "General",
                "content": "This is the main body content of our very first blog post. Django makes it extremely easy to build robust web applications with dynamic content systems.",
                "author": "Admin"
            },
            {
                "title": "The Art of Deconstruction: Designing Capsule 01",
                "chead": "A look inside the design studio as we map out core elements and materials.",
                "category": "Design",
                "content": "Exploring the raw color architecture, heavyweight materials, and physical design philosophy behind our latest seasonal capsule release.",
                "author": "Velouria Studio"
            },
            {
                "title": "Behind the Frame: Engineering Fluid Interactions",
                "chead": "How we built a frictionless, zero-latency digital storefront experience.",
                "category": "Technology",
                "content": "Leveraging minimal front-end architectures and asynchronous state machines to power zero-latency shopping experiences.",
                "author": "Engineering Team"
            }
        ]

        created_prods = 0
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
                created_prods += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Seeded Product: {product.product_name}'))
            else:
                self.stdout.write(self.style.NOTICE(f'  [--] Skip Product (exists): {product.product_name}'))

        created_posts = 0
        for post_item in starter_posts:
            post, created = BlogPost.objects.get_or_create(
                title=post_item["title"],
                defaults={
                    "chead": post_item["chead"],
                    "category": post_item["category"],
                    "content": post_item["content"],
                    "author": post_item["author"],
                    "pub_date": timezone.now().date(),
                },
            )
            if created:
                created_posts += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Seeded Post: {post.title} ({post.category})'))
            else:
                self.stdout.write(self.style.NOTICE(f'  [--] Skip Post (exists): {post.title}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nData ingestion complete! {created_prods} product(s) & {created_posts} blog post(s) added.')
        )
