from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import Category, Product, ProductImage


CATEGORIES = [
    ("Style", "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=85"),
    ("Technology", "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1200&q=85"),
    ("Home", "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=85"),
    ("Wellness", "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1200&q=85"),
    ("Travel", "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=85"),
    ("Accessories", "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=1200&q=85"),
]


PRODUCTS = [
    {
        "category": "Style", "name": "Heritage Leather Tote", "price": "4890", "previous_price": "5590", "stock": 18,
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 128,
        "short": "A softly structured everyday tote in rich, responsibly finished leather.",
        "description": "Designed to move easily from workdays to weekends, the Heritage Tote balances generous capacity with a clean, enduring silhouette. A secure inner pocket keeps essentials close while reinforced handles make it comfortable to carry all day.\n\nThe warm grain develops character over time, making every bag quietly individual.",
    },
    {
        "category": "Style", "name": "Coastal Linen Overshirt", "price": "2790", "previous_price": None, "stock": 32,
        "image": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 64,
        "short": "An airy layering piece with relaxed tailoring and natural texture.",
        "description": "Cut for an easy, modern fit, this breathable overshirt brings polish without stiffness. Wear it open over a tee or buttoned for a refined, understated look.\n\nIts versatile neutral tone pairs naturally with denim, chinos, and relaxed tailoring.",
    },
    {
        "category": "Style", "name": "Meridian Everyday Sneakers", "price": "4290", "previous_price": "4890", "stock": 21,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.8", "reviews": 203,
        "short": "Clean-lined sneakers with cloud-soft cushioning for all-day movement.",
        "description": "The Meridian blends a streamlined profile with dependable comfort. A cushioned footbed and flexible sole support long city days while the minimal upper keeps every outfit feeling considered.\n\nBuilt as a true everyday staple with an easy-to-clean finish.",
    },
    {
        "category": "Style", "name": "Silk-Touch Studio Scarf", "price": "1650", "previous_price": None, "stock": 40,
        "image": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.6", "reviews": 37,
        "short": "A fluid printed scarf that adds a refined finishing note.",
        "description": "Lightweight with a subtle sheen, the Studio Scarf is made to be worn at the neck, on a bag, or as a hair accent. Its modern geometric print brings personality while remaining effortless to style.",
    },
    {
        "category": "Technology", "name": "Arc Wireless Headphones", "price": "6590", "previous_price": "7290", "stock": 15,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 312,
        "short": "Immersive wireless sound with a calm, comfortable over-ear fit.",
        "description": "Arc headphones pair balanced audio with soft memory-foam cushions and up to 30 hours of listening. Simple on-ear controls keep calls, music, and focus sessions beautifully uninterrupted.\n\nUSB-C fast charging provides hours of playback from a short top-up.",
    },
    {
        "category": "Technology", "name": "Halo Compact Desk Speaker", "price": "3850", "previous_price": None, "stock": 26,
        "image": "https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 91,
        "short": "Room-filling sound in a sculptural, space-conscious form.",
        "description": "Made for desks, nightstands, and smaller rooms, Halo delivers warm sound without visual clutter. Bluetooth pairing is instant, controls are intuitive, and the tactile woven finish feels at home in thoughtful interiors.",
    },
    {
        "category": "Technology", "name": "Slate Active Smartwatch", "price": "7490", "previous_price": "8390", "stock": 12,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.8", "reviews": 174,
        "short": "A refined daily smartwatch for movement, focus, and connection.",
        "description": "Slate tracks essential wellness metrics, workouts, sleep, and notifications through a crisp, always-on display. The slim case and soft-touch strap transition easily from training sessions to workdays.\n\nWater resistant and designed for multi-day battery life.",
    },
    {
        "category": "Technology", "name": "Orbit 3-in-1 Charging Dock", "price": "2890", "previous_price": None, "stock": 34,
        "image": "https://images.unsplash.com/photo-1587033411391-5d9e51cce126?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.6", "reviews": 58,
        "short": "A minimal bedside dock for your phone, watch, and earbuds.",
        "description": "Orbit replaces cable clutter with one compact charging home. Its weighted base stays secure on the desk while softly angled surfaces keep devices visible and easy to reach.",
    },
    {
        "category": "Home", "name": "Aura Sculptural Table Lamp", "price": "3590", "previous_price": "4190", "stock": 17,
        "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 86,
        "short": "A warm, ambient lamp with a softly architectural silhouette.",
        "description": "Aura turns a practical light source into a quiet focal point. Its diffused glow is ideal for reading corners and bedside tables, while the matte finish complements both minimal and layered rooms.\n\nIncludes a warm LED bulb for an inviting atmosphere from day one.",
    },
    {
        "category": "Home", "name": "Cloud Woven Throw", "price": "2450", "previous_price": None, "stock": 28,
        "image": "https://images.unsplash.com/photo-1580301762395-21ce84d00bc6?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.8", "reviews": 72,
        "short": "A generously soft woven layer for sofas, reading chairs, and slow mornings.",
        "description": "The Cloud Throw brings breathable warmth and subtle texture to everyday spaces. Its neutral weave layers easily across changing seasons and finishes with a relaxed fringe detail.",
    },
    {
        "category": "Home", "name": "Cedar Mist Aroma Diffuser", "price": "2190", "previous_price": "2490", "stock": 25,
        "image": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 109,
        "short": "Whisper-quiet aromatherapy with a calming, wood-inspired finish.",
        "description": "Create a more grounded atmosphere with fine, cool mist and adjustable ambient light. The diffuser runs quietly for work, rest, or evening rituals and switches off automatically when empty.",
    },
    {
        "category": "Home", "name": "Form Hand-Finished Ceramic Vase", "price": "1890", "previous_price": None, "stock": 0,
        "image": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.6", "reviews": 41,
        "short": "An organic ceramic vessel with quiet texture and modern proportion.",
        "description": "Each Form vase carries subtle variations that celebrate its hand-finished character. Display it with a single branch, a relaxed bouquet, or entirely on its own as an understated sculptural object.",
    },
    {
        "category": "Wellness", "name": "Align Performance Yoga Mat", "price": "2490", "previous_price": "2790", "stock": 22,
        "image": "https://images.unsplash.com/photo-1592432678016-e910b452f9a2?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.8", "reviews": 149,
        "short": "Supportive grip and balanced cushioning for a more focused practice.",
        "description": "Align provides a stable, non-slip surface through restorative stretches and faster flows. Its dense cushioning protects joints without compromising grounded balance.\n\nThe easy-clean finish and included carry strap make daily practice simpler.",
    },
    {
        "category": "Wellness", "name": "Restore Mini Massage Gun", "price": "8990", "previous_price": "9990", "stock": 11,
        "image": "https://images.unsplash.com/photo-1591343395082-e120087004b4?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 188,
        "short": "Targeted muscle relief in a compact, remarkably quiet design.",
        "description": "Restore offers four intensity levels and a balanced grip for comfortable recovery at home or on the move. Its low-noise motor keeps relaxation genuinely relaxing, while interchangeable heads support different muscle groups.",
    },
    {
        "category": "Wellness", "name": "Calm Tea Ritual Set", "price": "1590", "previous_price": None, "stock": 36,
        "image": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 53,
        "short": "A serene stoneware tea set made for unhurried daily pauses.",
        "description": "The Calm set includes a balanced teapot, two handleless cups, and a fine stainless infuser. Soft glaze and natural tonal variation give every pour a tactile, grounded quality.",
    },
    {
        "category": "Wellness", "name": "Pure Borosilicate Water Bottle", "price": "990", "previous_price": None, "stock": 48,
        "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.5", "reviews": 68,
        "short": "A clean-tasting glass bottle protected by a soft silicone sleeve.",
        "description": "Pure keeps water fresh without retaining flavours. The protective sleeve improves grip, the leak-resistant cap travels confidently, and clear volume markers make mindful hydration easier.",
    },
    {
        "category": "Travel", "name": "Voyager Urban Cabin Backpack", "price": "5490", "previous_price": "6290", "stock": 19,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 221,
        "short": "A smart cabin-ready backpack with thoughtful organization throughout.",
        "description": "Voyager opens flat for efficient packing and includes dedicated spaces for a laptop, documents, and smaller essentials. Padded straps and a breathable back panel keep longer journeys comfortable.\n\nIts water-resistant shell handles daily commutes and weekend departures with equal ease.",
    },
    {
        "category": "Travel", "name": "Drift Canvas Weekender", "price": "4790", "previous_price": None, "stock": 16,
        "image": "https://images.unsplash.com/photo-1553735288-8f9899c16ad2?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 77,
        "short": "A relaxed, durable holdall sized for spontaneous weekends away.",
        "description": "Drift combines sturdy canvas with refined trims and a broad opening that makes packing effortless. Interior pockets separate smaller essentials, while reinforced handles and a removable shoulder strap offer flexible carrying.",
    },
    {
        "category": "Travel", "name": "Nomad Packing Cube Set", "price": "1390", "previous_price": "1590", "stock": 42,
        "image": "https://images.unsplash.com/photo-1553531889-56d1e30010ec?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.6", "reviews": 95,
        "short": "Three lightweight organizers for calmer, more efficient packing.",
        "description": "The Nomad set keeps clothing, accessories, and laundry neatly separated. Breathable mesh panels reveal contents at a glance, while smooth two-way zips make every cube easy to access.",
    },
    {
        "category": "Travel", "name": "Atlas Insulated Travel Tumbler", "price": "1290", "previous_price": None, "stock": 50,
        "image": "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.7", "reviews": 120,
        "short": "A leak-resistant tumbler that keeps everyday drinks at their best.",
        "description": "Double-wall insulation keeps drinks hot or cold for hours, while the slim base fits most cup holders. The textured finish feels secure in hand and the simple lid is easy to clean.",
    },
    {
        "category": "Accessories", "name": "Solstice Polarized Sunglasses", "price": "2290", "previous_price": "2690", "stock": 31,
        "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.8", "reviews": 133,
        "short": "Timeless polarized frames with a flattering, softly sculpted profile.",
        "description": "Solstice filters glare and provides full UV protection through lenses designed for clear, comfortable vision. The lightweight frame balances classic shape with subtle contemporary lines.",
    },
    {
        "category": "Accessories", "name": "Classic Minimal Watch", "price": "5890", "previous_price": "6490", "stock": 14,
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=1000&q=85", "featured": True, "rating": "4.9", "reviews": 167,
        "short": "A refined everyday timepiece with a crisp dial and supple leather strap.",
        "description": "Classic is intentionally understated: a slim case, clean markers, and precise quartz movement. The genuine leather strap softens with wear, making it a natural companion for work, evenings, and everything between.",
    },
    {
        "category": "Accessories", "name": "Atelier Leather Card Holder", "price": "1490", "previous_price": None, "stock": 39,
        "image": "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.6", "reviews": 49,
        "short": "A slim leather card case with considered storage and hand-finished edges.",
        "description": "Atelier carries the essentials without bulk. Four external slots and a central pocket hold cards and folded notes, while fine stitching and burnished edges add lasting refinement.",
    },
    {
        "category": "Accessories", "name": "Muse Pearl Drop Earrings", "price": "1990", "previous_price": "2290", "stock": 27,
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=1000&q=85", "featured": False, "rating": "4.8", "reviews": 82,
        "short": "Luminous pearl drops with a delicate, modern sense of movement.",
        "description": "Muse reimagines a classic pearl earring with clean proportions and gentle movement. Light enough for extended wear, they bring an elegant finishing note to both simple daytime looks and evening dressing.",
    },
]


GALLERY_IMAGES = {
    "heritage-leather-tote": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?auto=format&fit=crop&w=1000&q=85",
    "meridian-everyday-sneakers": "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=1000&q=85",
    "arc-wireless-headphones": "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=1000&q=85",
    "slate-active-smartwatch": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?auto=format&fit=crop&w=1000&q=85",
    "aura-sculptural-table-lamp": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=1000&q=85",
    "align-performance-yoga-mat": "https://images.unsplash.com/photo-1603988363607-e1e4a66962c6?auto=format&fit=crop&w=1000&q=85",
    "voyager-urban-cabin-backpack": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=1000&q=85",
    "classic-minimal-watch": "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?auto=format&fit=crop&w=1000&q=85",
}


class Command(BaseCommand):
    help = "Create or update EA Mart's 24-product demo catalogue."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete current products and categories before seeding.")

    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing catalogue cleared."))

        category_objects = {}
        for name, image_url in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "image_url": image_url},
            )
            category_objects[name] = category

        for data in PRODUCTS:
            product, _ = Product.objects.update_or_create(
                slug=slugify(data["name"]),
                defaults={
                    "category": category_objects[data["category"]],
                    "name": data["name"],
                    "short_description": data["short"],
                    "description": data["description"],
                    "price": Decimal(data["price"]),
                    "previous_price": Decimal(data["previous_price"]) if data["previous_price"] else None,
                    "stock_quantity": data["stock"],
                    "image_url": data["image"],
                    "rating": Decimal(data["rating"]),
                    "review_count": data["reviews"],
                    "is_featured": data["featured"],
                    "is_active": True,
                },
            )
            gallery_url = GALLERY_IMAGES.get(product.slug)
            if gallery_url:
                ProductImage.objects.update_or_create(
                    product=product,
                    image_url=gallery_url,
                    defaults={"alt_text": f"Alternate view of {product.name}"},
                )

        self.stdout.write(self.style.SUCCESS(f"EA Mart catalogue ready: {Product.objects.count()} products across {Category.objects.count()} categories."))
