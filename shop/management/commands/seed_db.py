from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.models import Product  
from blog.models import BlogPost  

class Command(BaseCommand):
    help = 'Flushes old stock/logs and seeds both products and blog posts with matching boutique data'

    def handle(self, *args, **kwargs):
        # 🗑️ WIPE OUT THE PAST
        self.stdout.write(self.style.WARNING('Flushing previous products and old blog entries...'))
        Product.objects.all().delete()
        BlogPost.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Databases cleared completely.'))

        today = timezone.now().date()

        # ==========================================
        # 🧴 1. SEED EXPANDED BOUTIQUE PRODUCT STOCK (15 SKUs)
        # ==========================================
        boutique_products = [
            # === SKINCARE CAPSULE ===
            {"product_name": "Nourishing Botanical Face Oil", "category": "Skincare", "price": 850, "desc": "A weightless blend of cold-pressed jojoba and squalane infused with organic rosehip to deeply hydrate and restore natural radiance.", "image": "shop/images/face_oil.png"},
            {"product_name": "Pink French Clay Mask", "category": "Skincare", "price": 620, "desc": "Formulated with superfine red and white clays to gently detoxify skin texture, drawing out impurities while maintaining natural moisture.", "image": "shop/images/clay_mask.png"},
            {"product_name": "Vitamin C Glow Serum", "category": "Skincare", "price": 1150, "desc": "A daily brightening matrix concentrated with Kakadu plum extract and hyaluronic acid to even out skin tone and defend daily vitality layers.", "image": "shop/images/serum.png"},
            {"product_name": "Bakuchiol Alternative Retinol Ampoule", "category": "Skincare", "price": 1380, "desc": "A plant-based, non-irritating retinol alternative complex target-engineered to refine fine lines and smooth overall structural skin profile.", "image": "shop/images/bakuchiol.png"},
            {"product_name": "Ceramide Barrier Repair Balm", "category": "Skincare", "price": 740, "desc": "An ultra-rich, lipid-replenishing moisture barrier balm containing pure oat kernels to protect sensitive or stressed complexions.", "image": "shop/images/barrier_balm.png"},
            
            # === FRAGRANCE CAPSULE ===
            {"product_name": "Smoked Santal Soy Candle", "category": "Fragrance", "price": 780, "desc": "Hand-poured pure soy wax candle featuring complex heart notes of Australian sandalwood, cardamon, and warm amber accords.", "image": "shop/images/candle_santal.png"},
            {"product_name": "Wild Lavender Reed Diffuser", "category": "Fragrance", "price": 950, "desc": "An elegant glass vessel dispersing steam-distilled lavender essence continuously through natural rattan reeds for calming spaces.", "image": "shop/images/diffuser.png"},
            {"product_name": "Eucalyptus & White Sage Room Mist", "category": "Fragrance", "price": 420, "desc": "An instantly refreshing atmospheric home mist utilizing wild-harvested desert sage to purify spatial air profile layers dynamically.", "image": "shop/images/sage_mist.png"},
            {"product_name": "Velvet Moss & Amber Incense Cones", "category": "Fragrance", "price": 380, "desc": "A box of 20 slow-burning charcoal cones saturated with deep tree moss, rich amber resins, and soft vanilla extract notes.", "image": "shop/images/incense.png"},
            {"product_name": "Bergamot & Tobacco Leaf Soy Block", "category": "Fragrance", "price": 680, "desc": "A heavy, sculptural wax melt blocks profile releasing notes of bright Italian bergamot balanced against sweet crushed tobacco leaves.", "image": "shop/images/wax_melt.png"},

            # === APOTHECARY CAPSULE ===
            {"product_name": "Crushed Coconut Body Scrub", "category": "Apothecary", "price": 540, "desc": "Gently exfoliating crystalline raw cane sugar base blended thoroughly with organic virgin coconut oil and nourishing vitamin E lipids.", "image": "shop/images/body_scrub.png"},
            {"product_name": "Himalayan Cedarwood Bath Salts", "category": "Apothecary", "price": 480, "desc": "Mineral-rich pink salt crystals saturated with pure essential oils of grounding Himalayan cedarwood and refreshing bergamot.", "image": "shop/images/bath_salts.png"},
            {"product_name": "Shea Butter Botanical Bar Soap", "category": "Apothecary", "price": 280, "desc": "A cold-processed, triple-milled body bar enriched with raw African shea butter and decorated with dried calendula petals.", "image": "shop/images/soap_bar.png"},
            {"product_name": "Rejuvenating Mint Foot Cream", "category": "Apothecary", "price": 490, "desc": "A rich, deeply therapeutic foot balm blending high-potency cooling peppermint oil alongside pure tea tree extracts.", "image": "shop/images/foot_cream.png"},
            {"product_name": "Soothing Sweet Almond Body Lotion", "category": "Apothecary", "price": 890, "desc": "A velvety body moisturizer combining sweet organic almond milk base with rich cold-pressed avocado oil drops.", "image": "shop/images/body_lotion.png"}
        ]

        for item in boutique_products:
            Product.objects.create(
                product_name=item["product_name"],
                category=item["category"],
                subcategory="Boutique",
                price=item["price"],
                description=item["desc"],
                image=item["image"],
                pub_date=today,
                stock=50
            )
        self.stdout.write(self.style.SUCCESS('15 Premium Boutique SKUs Hydrated.'))

        # ==========================================
        # 📰 2. SEED EDITORIAL BOUTIQUE BLOG POSTS
        # ==========================================
        boutique_blogs = [
            {
                "title": "The Art of Slow Rituals: Building a Conscious Skincare Matrix",
                "subheading": "Moving past aggressive treatments to support and respect your skin barrier.",
                "category": "Skincare",
                "content": """Skincare isn't an aggressive chore; it is an intentional ritual of restoration. For too long, standard beauty protocols pushed harsh chemical peels that stripped our natural protective lipids. Today, we are stepping back into the science of slow skincare. 

Our formulation methodology focuses entirely on biological compatibility. By feeding your skin natural moisture anchors like squalane—found directly in our **Nourishing Botanical Face Oil**—you assist your skin in locking in cell hydration without choking your pores. When paired with botanical micro-minerals like our superfine **Pink French Clay Mask**, you create a balanced ecosystem that cleanses gently while keeping your natural moisture barrier completely unbothered.""",
                "thumbnail": "blog/images/skincare_ritual.jpg"
            },
            {
                "title": "OQIREL Architecture: How Home Fragrance Shapes Mental Spaces",
                "subheading": "Understanding the neuro-OQIREL connection behind clean ambient wood accords.",
                "category": "Fragrance",
                "content": """The atmosphere of your living room dictating your psychological calm isn't a myth—it is sensory science. When we inhale natural scent formulations, the volatile molecules directly interact with our limbic system, the sector of the brain managing emotional memory banks.

To curate an environment optimized for focus and deep resetting, look toward rich, grounding wood materials. Burning a premium, hand-poured candle like the **Smoked Santal Soy Candle** introduces dense heart notes of raw Australian sandalwood and cardamon that actively trigger neural decompression signals. For continuous spatial harmony without flame hazards, setting a **Wild Lavender Reed Diffuser** in high-airflow areas gently circulates steam-distilled botanicals to ground your daily routine.""",
                "thumbnail": "blog/images/fragrance_science.jpg"
            },
            {
                "title": "Apothecary Essentials: The Remedial Power of Mineral-Rich Soaking",
                "subheading": "Why transdermal magnesium salts and raw plant lipid bars beat synthetic washes.",
                "category": "Apothecary",
                "content": """Your skin is your largest structural organ, absorbing everything it contacts. Mass-market body gels are frequently packed with aggressive sodium lauryl sulfates (SLS) that compromise cell junctions and leave your skin tight and parched. Shifting to an apothecary-first bath system returns to pure, unadulterated ingredients.

Immersing yourself in warm water infused with our coarse **Himalayan Cedarwood Bath Salts** allows rich trace minerals to absorb transdermally, promoting muscular relief. Follow up this reset by utilizing cold-processed options like our **Shea Butter Botanical Bar Soap**. Because it is triple-milled and packed with natural African shea lipids, it cleanses without deleting your skin's vital moisture sheets.""",
                "thumbnail": "blog/images/bath_apothecary.jpg"
            }
        ]

        # Loop and safely insert blog objects into your database
        for entry in boutique_blogs:
            BlogPost.objects.create(
                title=entry["title"],
                chead=entry["subheading"],
                category=entry["category"],
                author="Editorial Team",
                content=entry["content"],
                pub_date=today,
                thumbnail=entry["thumbnail"]
            )
        
        self.stdout.write(self.style.SUCCESS('Dynamic Editorial Blog Journal Hydrated Flawlessly!'))
