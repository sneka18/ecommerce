"""
Database Initialization and Data Seeding Script
Creates all tables and seeds realistic categories, demo products, sellers, users, and interactions.
"""
import sys
from datetime import datetime, timezone, timedelta
from app.database import engine, SessionLocal, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.seller import Seller
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.review import ProductReview
from app.models.interaction import UserInteraction


def init_database():
    print("=" * 60)
    print("Initializing Database Tables...")
    print("=" * 60)

    try:
        # Create all tables defined in Base
        Base.metadata.create_all(bind=engine)
        print(" All tables created / verified successfully in MySQL!")
    except Exception as e:
        print(f" ERROR creating database tables: {e}")
        print("Please ensure your MySQL service is running and DB_PASSWORD in Backend/.env is correct.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Check if already seeded
        admin_exists = db.query(User).filter(User.email == "admin@ecommerce.com").first()
        if admin_exists:
            print(" Database already contains seed data. Skipping seed step.")
            return

        print("\nSeeding initial data (Roles, Categories, Products, Interactions)...")

        # 1. Create Admin
        admin = User(
            email="admin@ecommerce.com",
            password_hash=hash_password("AdminPassword123!"),
            full_name="System Administrator",
            phone="+1234567890",
            role="admin",
            is_active=True
        )
        db.add(admin)

        # 2. Create Sellers
        seller_user1 = User(
            email="seller@techhub.com",
            password_hash=hash_password("SellerPassword123!"),
            full_name="Alex Turner",
            phone="+1987654321",
            role="seller",
            is_active=True
        )
        db.add(seller_user1)
        db.flush()

        seller_profile1 = Seller(
            user_id=seller_user1.id,
            store_name="TechHub Electronics",
            store_description="Premier destination for cutting-edge gadgets, audio gear, and smart electronics.",
            business_email="support@techhub.com",
            phone="+1987654321",
            address="100 Silicon Way, San Jose, CA",
            is_approved=True
        )
        db.add(seller_profile1)

        seller_user2 = User(
            email="seller@stylezone.com",
            password_hash=hash_password("SellerPassword123!"),
            full_name="Elena Vance",
            phone="+14155551234",
            role="seller",
            is_active=True
        )
        db.add(seller_user2)
        db.flush()

        seller_profile2 = Seller(
            user_id=seller_user2.id,
            store_name="StyleZone Lifestyle",
            store_description="Curated contemporary fashion, lifestyle essentials, and modern home accessories.",
            business_email="contact@stylezone.com",
            phone="+14155551234",
            address="45 Fashion Blvd, New York, NY",
            is_approved=True
        )
        db.add(seller_profile2)

        # 3. Create Customers
        customer1 = User(
            email="john@example.com",
            password_hash=hash_password("Customer123!"),
            full_name="John Doe",
            phone="+15551234567",
            role="customer",
            is_active=True
        )
        customer2 = User(
            email="jane@example.com",
            password_hash=hash_password("Customer123!"),
            full_name="Jane Smith",
            phone="+15557654321",
            role="customer",
            is_active=True
        )
        customer3 = User(
            email="david@example.com",
            password_hash=hash_password("Customer123!"),
            full_name="David Miller",
            phone="+15559871234",
            role="customer",
            is_active=True
        )
        db.add_all([customer1, customer2, customer3])
        db.flush()

        # Create Cart for each customer
        for cust in [customer1, customer2, customer3]:
            db.add(Cart(user_id=cust.id))

        # 4. Create Categories
        categories_data = [
            ("Electronics", "electronics", "Laptops, smartphones, audio devices, and smart accessories.", "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500&q=80"),
            ("Fashion & Apparel", "fashion", "Trendy clothing, footwear, and designer apparel for all seasons.", "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&q=80"),
            ("Home & Living", "home-living", "Modern furniture, kitchen appliances, and cozy home decor.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500&q=80"),
            ("Sports & Fitness", "sports-fitness", "Athletic gear, fitness trackers, and outdoor recreation equipment.", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80"),
            ("Books & Stationery", "books-stationery", "Bestselling books, journals, productivity tools, and supplies.", "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&q=80")
        ]

        cat_objs = {}
        for name, slug, desc, img in categories_data:
            cat = Category(name=name, slug=slug, description=desc, image_url=img)
            db.add(cat)
            db.flush()
            cat_objs[slug] = cat

        # 5. Seed Products
        products_data = [
            # Electronics (Seller 1)
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["electronics"].id,
                "name": "AuraSound Pro Wireless Noise-Cancelling Headphones",
                "slug": "aurasound-pro-wireless-headphones",
                "price": 199.99,
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
                "description": "Experience pristine studio sound with industry-leading Active Noise Cancellation and ultra-plush memory foam cushions for all-day comfort.",
                "ai_description": "Engineered for discerning audiophiles and frequent travelers, the AuraSound Pro delivers rich, immersive sound with custom-tuned 40mm neodymium drivers. Integrated smart transparency mode allows seamless conversation without removing the headset.",
                "highlights": "• 40 Hours Continuous Battery Life\n• Hybrid Active Noise Cancellation (ANC)\n• Dual Multipoint Bluetooth 5.3\n• Fast USB-C Charging (10 mins = 4 hrs playtime)",
                "specifications": '{"Driver Size": "40mm", "Bluetooth": "5.3", "Battery Life": "40 hrs", "Weight": "250g", "Charging": "USB-C"}',
                "rating": 4.8,
                "num_reviews": 42
            },
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["electronics"].id,
                "name": "Nova UltraSlim 15.6-inch 4K OLED Laptop",
                "slug": "nova-ultraslim-4k-oled-laptop",
                "price": 1249.99,
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80",
                "description": "Power through demanding creative workflows and multitasking with an ultra-fast processor and breathtaking 4K OLED display.",
                "ai_description": "The Nova UltraSlim combines high-caliber computing performance with breathtaking visual fidelity. Designed for modern creators, coders, and power users seeking uncompromised portability and precision.",
                "highlights": "• 15.6\" 4K HDR OLED Screen\n• Intel Core i7 13th Gen with 16GB LPDDR5\n• 1TB NVMe PCIe 4.0 SSD\n• Thunderbolt 4 & Wi-Fi 6E Support",
                "specifications": '{"CPU": "Intel Core i7-13650H", "RAM": "16GB LPDDR5", "Storage": "1TB SSD", "Display": "15.6 inch 4K OLED", "OS": "Windows 11"}',
                "rating": 4.9,
                "num_reviews": 29
            },
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["electronics"].id,
                "name": "PulseFit Active Smartwatch with AMOLED Display",
                "slug": "pulsefit-active-smartwatch",
                "price": 129.50,
                "stock": 50,
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
                "description": "Track health metrics around the clock with SpO2 sensing, continuous heart rate tracking, and 100+ athletic training modes.",
                "ai_description": "A refined lifestyle companion featuring an always-on AMOLED touchscreen encased in aerospace-grade aluminum. Keep tabs on sleep phases, fitness stress indices, and instant notifications right on your wrist.",
                "highlights": "• 1.43\" High-Res AMOLED Touchscreen\n• 24/7 Heart Rate, SpO2 & Sleep Tracking\n• 5ATM Water Resistance (Swimmable)\n• 14-Day Battery Life on a Single Charge",
                "specifications": '{"Display": "1.43 AMOLED", "Waterproof": "5ATM", "Battery": "450mAh (14 days)", "Sensors": "Heart Rate, SpO2, Accelerometer"}',
                "rating": 4.6,
                "num_reviews": 68
            },
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["electronics"].id,
                "name": "EchoBeat Mini Waterproof Portable Bluetooth Speaker",
                "slug": "echobeat-mini-portable-speaker",
                "price": 49.99,
                "stock": 75,
                "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80",
                "description": "Compact speaker packing punchy 360-degree sound with deep bass and IPX7 rugged waterproof protection.",
                "ai_description": "Designed for poolside parties, beach trips, and outdoor adventures. Delivers rich, room-filling sound with enhanced low-end resonance and true wireless stereo pairing.",
                "highlights": "• IPX7 Fully Waterproof\n• 360-degree Dynamic Audio\n• 12 Hours Continuous Playback\n• Built-in Carabiner Strap",
                "specifications": '{"Output": "16W RMS", "Battery": "12 Hours", "Waterproof": "IPX7", "Bluetooth": "5.2"}',
                "rating": 4.5,
                "num_reviews": 54
            },
            # Fashion & Apparel (Seller 2)
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["fashion"].id,
                "name": "Classic Maverick Genuine Leather Jacket",
                "slug": "classic-maverick-leather-jacket",
                "price": 189.00,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&q=80",
                "description": "Handcrafted from premium full-grain lambskin leather with tailored moto styling and heavy-duty antique brass zippers.",
                "ai_description": "An iconic wardrobe essential blending rugged sophistication with unmatched durability. Designed to soften gracefully with age while offering thermal insulated comfort.",
                "highlights": "• 100% Genuine Full-Grain Lambskin\n• Satin-Lined Interior with Hidden Pocket\n• Antique Brass YKK Hardware\n• Tailored Modern Cut",
                "specifications": '{"Material": "100% Lambskin Leather", "Lining": "100% Polyester Satin", "Fit": "Regular Tailored", "Closure": "YKK Zipper"}',
                "rating": 4.7,
                "num_reviews": 31
            },
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["fashion"].id,
                "name": "UrbanAura Minimalist Breathable Running Sneakers",
                "slug": "urbanaura-minimalist-running-sneakers",
                "price": 84.99,
                "stock": 60,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
                "description": "Engineered knit upper with responsive cloud-foam sole cushioning designed for high performance running and casual streetwear.",
                "ai_description": "Stride in lightweight comfort with an aerodynamic design built to absorb impact and return kinetic energy. Breathable mesh keeps feet cool during strenuous activity.",
                "highlights": "• CloudFoam Responsive Cushioning\n• Seamless FlyKnit Breathable Upper\n• Ergonomic Arch Support\n• High-Traction Rubber Outsole",
                "specifications": '{"Weight": "230g", "Upper": "Engineered Mesh", "Sole": "EVA + Rubber", "Closure": "Lace-up"}',
                "rating": 4.8,
                "num_reviews": 89
            },
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["fashion"].id,
                "name": "Nordic Weave Merino Wool Crewneck Sweater",
                "slug": "nordic-weave-merino-wool-sweater",
                "price": 79.50,
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&q=80",
                "description": "Ultra-soft non-scratch 100% Australian Merino wool sweater featuring ribbed cuffs, hem, and a timeless Scandinavian silhouette.",
                "ai_description": "Naturally thermoregulating and odor-resistant, this luxury knit sweater keeps you warm without bulk. Perfect for effortless smart-casual layering.",
                "highlights": "• 100% Australian Extra-Fine Merino Wool\n• Naturally Temperature-Regulating\n• Anti-Pilling Tight Knit Finish\n• Machine Washable on Gentle Cycle",
                "specifications": '{"Fiber": "100% Merino Wool", "Knit Gauge": "12-gauge", "Fit": "Slim Contemporary"}',
                "rating": 4.6,
                "num_reviews": 23
            },
            # Home & Living (Seller 2)
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["home-living"].id,
                "name": "BaristaPro Italian Espresso & Cappuccino Machine",
                "slug": "baristapro-italian-espresso-machine",
                "price": 249.00,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80",
                "description": "Craft authentic café-quality espresso, silky lattes, and cappuccinos with 15-bar Italian pressure and commercial steam wand.",
                "ai_description": "Elevate your morning ritual with commercial-grade brewing at home. Thermo-block heating delivers water at the precise optimal temperature in under 45 seconds.",
                "highlights": "• 15-Bar High-Pressure Italian Pump\n• Integrated Swivel Milk Frothing Wand\n• Thermo-Block Fast Heating System\n• Removable 1.5L BPA-Free Water Reservoir",
                "specifications": '{"Pressure": "15 Bar", "Power": "1350W", "Tank Capacity": "1.5L", "Heating Time": "45 seconds"}',
                "rating": 4.9,
                "num_reviews": 57
            },
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["home-living"].id,
                "name": "Lumina Ceramic Ultrasonic Essential Oil Diffuser",
                "slug": "lumina-ultrasonic-essential-oil-diffuser",
                "price": 38.00,
                "stock": 45,
                "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=500&q=80",
                "description": "Handcrafted matte ceramic aromatherapy diffuser with soothing warm LED ambient lighting and whisper-quiet ultrasonic misting.",
                "ai_description": "Transform your living space into a tranquil spa sanctuary. Disperses delicate essential oil scents while humidifying dry indoor air quietly.",
                "highlights": "• Matte Glazed Handcrafted Ceramic Cover\n• 7 Ambient Color Lighting Modes\n• Automatic Waterless Safety Shut-off\n• 300ml Capacity (Up to 10 hrs run time)",
                "specifications": '{"Capacity": "300ml", "Coverage": "300 sq ft", "Noise": "<20dB", "Material": "Ceramic + BPA-free PP"}',
                "rating": 4.7,
                "num_reviews": 38
            },
            # Sports & Fitness (Seller 1)
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["sports-fitness"].id,
                "name": "ApexGrip Adjustable Dumbbell Set (5 - 52.5 lbs)",
                "slug": "apexgrip-adjustable-dumbbell-set",
                "price": 299.99,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=500&q=80",
                "description": "Replace 15 pairs of conventional weights with a rapid dial-selection mechanism. Ideal for home gym strength conditioning.",
                "ai_description": "Compact engineering meets heavy-duty performance. Smooth dial mechanism lets you switch resistance in seconds, maximizing workout intensity and saving floor space.",
                "highlights": "• Replaces 15 Individual Weight Sets\n• Weight Adjusts from 5 to 52.5 lbs in 2.5 lb increments\n• Laser-Etched Knurled Steel Grip\n• Heavy-Duty Molded Storage Trays Included",
                "specifications": '{"Weight Range": "5 to 52.5 lbs each", "Plates": "Durable steel with thermoplastic coat", "Dimensions": "15.75 x 8 x 9 inches"}',
                "rating": 4.9,
                "num_reviews": 47
            },
            {
                "seller_id": seller_profile1.id,
                "category_id": cat_objs["sports-fitness"].id,
                "name": "ZenFlow High-Density Non-Slip Eco Yoga Mat",
                "slug": "zenflow-high-density-eco-yoga-mat",
                "price": 42.00,
                "stock": 65,
                "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&q=80",
                "description": "6mm extra-thick biodegradable TPE yoga mat offering joint-friendly cushioning, textured non-slip grip, and carry strap.",
                "ai_description": "Engineered for optimal alignment and slip resistance even during intense hot yoga sessions. Free from toxic phthalates, PVC, and latex.",
                "highlights": "• Dual-Sided Non-Slip Texture\n• 6mm Joint Protection Cushioning\n• 100% Eco-Friendly Recyclable TPE\n• Includes Complimentary Carrying Sling",
                "specifications": '{"Thickness": "6mm", "Dimensions": "72 x 24 inches", "Material": "Eco-TPE", "Weight": "900g"}',
                "rating": 4.6,
                "num_reviews": 62
            },
            # Books & Stationery (Seller 2)
            {
                "seller_id": seller_profile2.id,
                "category_id": cat_objs["books-stationery"].id,
                "name": "Executive Hardcover Dotted Journal & Brass Pen Set",
                "slug": "executive-hardcover-journal-pen-set",
                "price": 32.50,
                "stock": 80,
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&q=80",
                "description": "160gsm bleed-proof bamboo paper journal bound in vegan leather, paired with a solid brass balanced rollerball pen.",
                "ai_description": "A refined notebook for visionary thinkers, planners, and creatives. Heavyweight archival paper prevents ink bleeding and feathering, providing a tactile writing experience.",
                "highlights": "• 160 GSM Bleedproof Archival Pages\n• Expandable Inner Pocket & Dual Ribbon Markers\n• Heavy Solid Brass Rollerball Pen Included\n• Lay-Flat 180° Smyth-Sewn Binding",
                "specifications": '{"Pages": "192 numbered pages", "Paper": "160 GSM Bamboo Paper", "Ruling": "5mm Dot Grid", "Pen": "Solid Brass Rollerball"}',
                "rating": 4.9,
                "num_reviews": 74
            }
        ]

        created_products = []
        for p in products_data:
            prod = Product(**p)
            db.add(prod)
            db.flush()
            created_products.append(prod)

        # 6. Seed Realistic User Interactions for ML Training
        print("Seeding initial user interaction history for KNN model training...")
        interactions = [
            # Customer 1 (John - tech enthusiast)
            (customer1.id, created_products[0].id, "purchase", 5.0),
            (customer1.id, created_products[1].id, "purchase", 5.0),
            (customer1.id, created_products[2].id, "view", 4.5),
            (customer1.id, created_products[3].id, "cart", 4.0),
            (customer1.id, created_products[9].id, "view", 4.0),

            # Customer 2 (Jane - fitness & lifestyle enthusiast)
            (customer2.id, created_products[2].id, "purchase", 4.5),
            (customer2.id, created_products[5].id, "purchase", 5.0),
            (customer2.id, created_products[9].id, "purchase", 5.0),
            (customer2.id, created_products[10].id, "cart", 4.5),
            (customer2.id, created_products[8].id, "view", 4.0),

            # Customer 3 (David - home & tech enthusiast)
            (customer3.id, created_products[0].id, "purchase", 4.5),
            (customer3.id, created_products[7].id, "purchase", 5.0),
            (customer3.id, created_products[8].id, "cart", 4.0),
            (customer3.id, created_products[11].id, "purchase", 5.0),
            (customer3.id, created_products[1].id, "view", 4.5),
        ]

        now = datetime.now(timezone.utc)
        for uid, pid, itype, score in interactions:
            interaction = UserInteraction(
                user_id=uid,
                product_id=pid,
                interaction_type=itype,
                rating=score,
                timestamp=now - timedelta(days=2)
            )
            db.add(interaction)

        # 7. Seed Reviews
        reviews = [
            (created_products[0].id, customer1.id, 5, "These headphones completely transformed my daily commute. The noise cancellation is unreal!"),
            (created_products[1].id, customer1.id, 5, "Blazing fast laptop. The 4K OLED screen is phenomenal for video editing and programming."),
            (created_products[5].id, customer2.id, 5, "Best running shoes I have owned. Super lightweight and very comfortable."),
            (created_products[7].id, customer3.id, 5, "Makes delicious espresso with rich crema every single morning. Solid build quality!"),
        ]

        for pid, uid, rating, comm in reviews:
            db.add(ProductReview(product_id=pid, user_id=uid, rating=rating, comment=comm))

        # 8. Seed sample Orders
        order1 = Order(
            user_id=customer1.id,
            total_amount=created_products[0].price,
            shipping_address="123 Tech Lane, Austin, TX 78701",
            payment_method="Cash on Delivery",
            payment_status="Paid",
            status="Delivered"
        )
        db.add(order1)
        db.flush()

        order_item1 = OrderItem(
            order_id=order1.id,
            product_id=created_products[0].id,
            seller_id=created_products[0].seller_id,
            quantity=1,
            price=created_products[0].price
        )
        db.add(order_item1)

        db.commit()
        print(" Seed data successfully committed to database!")

    except Exception as e:
        db.rollback()
        print(f" Failed to seed database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

