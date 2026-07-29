import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAC.settings')
django.setup()

from blog.models import BlogPost

posts_data = [
    {
        "title": "Initializing the Ecosystem: The OQIREL Blueprint",
        "chead": "Architectural integrity meets weightless interface aesthetics.",
        "category": "Vision",
        "author": "OQIREL Team",
        "pub_date": date(2026, 7, 28),
        "content": (
            "Welcome to the nerve center of our digital experiment. OQIREL was built on a simple premise: "
            "e-commerce should feel less like an uninspired spreadsheet grid and more like an immersive design canvas.\n\n"
            "By ditching standard monolithic styling structures for a high-contrast editorial color scheme—anchored "
            "by custom earth tones, muted pink highlights, and asynchronous frontend interface mechanics—we have created "
            "an online space that treats products like physical gallery pieces. This journal is where we document "
            "our development sprints, design failures, and victories as we continue to push production-grade full-stack "
            "features live."
        )
    },
    {
        "title": "Shipping Asynchronous Commerce: The Technical Blueprint",
        "chead": "How we optimized client-side state execution to deliver a zero-latency shop drawer.",
        "category": "Engineering",
        "author": "Engineering Team",
        "pub_date": date(2026, 7, 27),
        "content": (
            "A major update has officially been merged into our master branch infrastructure. In this log, we break down "
            "the deployment of our new slide-out mini-cart drawer layer.\n\n"
            "By leveraging jQuery event delegation matrices alongside persistent client-side localStorage tokens, "
            "users can now adjust product volumes and verify shipping balance margins dynamically without triggering "
            "standard page refreshes. This significantly cuts down redundant server queries to our PostgreSQL database "
            "tables during high-velocity customer sessions, making the entire platform feel hyper-optimized, fast, "
            "and entirely compliant with modern production standards."
        )
    },
    {
        "title": "Securing the Pipeline: Moving to Cloud Environments",
        "chead": "Migrating local frameworks onto managed hosting servers.",
        "category": "Operations",
        "author": "DevOps Team",
        "pub_date": date(2026, 7, 26),
        "content": (
            "We are officially live in production. This week marked the successful migration of our system onto "
            "the Render cloud hosting infrastructure.\n\n"
            "To ensure institutional security standards, we completely decoupled all sensitive access data—moving "
            "our core Django secret configurations, external Razorpay payment gateway credentials, and PostgreSQL "
            "connection keys entirely into environment variables handled via python-dotenv. Backed by a custom "
            "WhiteNoise integration engine that handles aggressive compression and asset caching, the storefront "
            "is now completely hardened against vectors and optimized for production traffic speeds."
        )
    }
]

def populate():
    created_count = 0
    for p in posts_data:
        post, created = BlogPost.objects.get_or_create(
            title=p["title"],
            defaults={
                "chead": p["chead"],
                "category": p["category"],
                "author": p["author"],
                "pub_date": p["pub_date"],
                "content": p["content"]
            }
        )
        if created:
            created_count += 1
            print(f"Created post: '{post.title}' (ID: {post.post_id})")
        else:
            # Update existing post if content changed
            post.chead = p["chead"]
            post.category = p["category"]
            post.author = p["author"]
            post.pub_date = p["pub_date"]
            post.content = p["content"]
            post.save()
            print(f"Updated post: '{post.title}' (ID: {post.post_id})")
            
    print(f"Done! {len(posts_data)} posts processed.")

if __name__ == "__main__":
    populate()
