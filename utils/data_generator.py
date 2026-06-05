"""
Data generation script for SmartRecommend
Generates realistic Nigerian e-commerce dataset
"""
import pandas as pd
import numpy as np
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Product catalog ───────────────────────────────────────────────────────────
PRODUCTS_DATA = {
    "Smartphones": [
        ("Samsung Galaxy S24 Ultra 5G", 1350000, 4.8, "Samsung's flagship with 200MP camera, S-Pen, AI features, 5000mAh battery, Snapdragon 8 Gen 3"),
        ("iPhone 15 Pro Max", 1650000, 4.7, "Apple's premium smartphone with titanium design, A17 Pro chip, 48MP camera system, USB-C"),
        ("Samsung Galaxy A54", 420000, 4.5, "Mid-range Samsung with 50MP camera, 5000mAh battery, 6.4-inch Super AMOLED display"),
        ("Tecno Camon 30 Pro", 185000, 4.3, "Tecno flagship with 50MP portrait camera, 5000mAh battery, MediaTek Helio G99"),
        ("Infinix Note 40 Pro", 175000, 4.2, "6.78-inch display, 108MP camera, 45W fast charging, Helio G99 Ultra processor"),
        ("iPhone 14", 950000, 4.6, "Apple iPhone 14 with A15 Bionic, 12MP dual camera, Crash Detection, Emergency SOS"),
        ("Xiaomi 14 Ultra", 1100000, 4.7, "Leica quad camera, Snapdragon 8 Gen 3, 90W HyperCharge, 5000mAh battery"),
        ("Samsung Galaxy S23 FE", 600000, 4.4, "Fan Edition with Snapdragon 8 Gen 1, 50MP camera, 4500mAh battery, IP68 rating"),
        ("Oppo Reno 11 Pro", 380000, 4.3, "50MP triple camera, 80W SuperVOOC charging, 6.7-inch curved AMOLED, 4600mAh"),
        ("Google Pixel 8 Pro", 1200000, 4.6, "Google Tensor G3, 50MP camera with AI features, 7 years of updates, 5050mAh"),
        ("Vivo V30 Pro", 350000, 4.2, "50MP IMX920 camera, Dimensity 8200, 80W FlashCharge, 4600mAh battery"),
        ("Realme GT 5 Pro", 480000, 4.4, "Snapdragon 8 Gen 3, 50MP Sony IMX890, 100W fast charging, 5400mAh battery"),
        ("Nokia G42 5G", 135000, 4.0, "Snapdragon 480+ 5G, repairability focus, 50MP camera, 5000mAh, Nokia 3-year guarantee"),
        ("Motorola Edge 40 Pro", 520000, 4.3, "Snapdragon 8 Gen 2, 165Hz pOLED, 125W TurboPower charging, 4600mAh battery"),
        ("OnePlus 12", 890000, 4.6, "Snapdragon 8 Gen 3, Hasselblad camera, 100W SUPERVOOC, 5400mAh, 120Hz ProXDR"),
        ("Tecno Phantom X2 Pro", 280000, 4.4, "Retractable portrait lens, Dimensity 9000, 5160mAh battery, 45W charging"),
        ("Itel P55+", 65000, 3.9, "Budget 4G phone, 6000mAh battery, 6.6-inch display, 13MP camera, Android 13"),
        ("Samsung Galaxy Z Fold 5", 2100000, 4.5, "Foldable flagship, 7.6-inch inner display, S-Pen ready, Snapdragon 8 Gen 2"),
        ("Huawei Pura 70 Pro", 980000, 4.5, "Kirin 9010, variable aperture lens, 80W fast charging, satellite messaging"),
        ("Sony Xperia 1 VI", 1250000, 4.4, "21:9 4K OLED, Snapdragon 8 Gen 3, pro camera controls, 5000mAh, 30W charge"),
    ],
    "Laptops": [
        ("HP Pavilion 15 Laptop", 850000, 4.6, "Intel Core i7 12th Gen, 16GB RAM, 512GB SSD, 15.6-inch FHD display, Windows 11"),
        ("MacBook Pro 14 M3", 1980000, 4.9, "Apple M3 Pro chip, 18GB RAM, 512GB SSD, 14.2-inch Liquid Retina XDR, 18hr battery"),
        ("Dell XPS 15", 1450000, 4.7, "Intel Core i9, 32GB RAM, 1TB SSD, 15.6-inch OLED touchscreen, NVIDIA RTX 4070"),
        ("Lenovo IdeaPad 3", 620000, 4.3, "AMD Ryzen 5 7520U, 8GB RAM, 256GB SSD, 15.6-inch FHD, Windows 11 Home"),
        ("Asus ROG Strix G16", 1750000, 4.6, "Intel Core i9-13980HX, 16GB RAM, 1TB SSD, RTX 4070, 16-inch 240Hz QHD"),
        ("MacBook Air M2", 1350000, 4.8, "Apple M2 chip, 8GB RAM, 256GB SSD, 13.6-inch Liquid Retina, 18-hour battery"),
        ("Acer Aspire 5", 580000, 4.2, "Intel Core i5 12th Gen, 8GB RAM, 512GB SSD, 15.6-inch FHD, backlit keyboard"),
        ("HP EliteBook 840 G10", 1100000, 4.5, "Intel Core i7-1365U, 16GB RAM, 512GB SSD, 14-inch IPS, vPro security features"),
        ("Dell Inspiron 15", 720000, 4.3, "Intel Core i5-1335U, 16GB RAM, 512GB SSD, 15.6-inch FHD, Windows 11, webcam"),
        ("Lenovo ThinkPad X1 Carbon", 1650000, 4.7, "Intel Core i7-1365U, 16GB RAM, 1TB SSD, 14-inch IPS, legendary keyboard, MIL-SPEC"),
        ("Microsoft Surface Laptop 5", 1200000, 4.5, "Intel Core i7, 16GB RAM, 512GB SSD, 13.5-inch PixelSense, Windows 11 Pro"),
        ("HP Spectre x360", 1380000, 4.6, "Intel Core i7-1355U, 16GB RAM, 1TB SSD, 14-inch OLED touchscreen, 2-in-1 design"),
        ("Asus VivoBook 15", 520000, 4.2, "Intel Core i5 11th Gen, 8GB RAM, 512GB SSD, 15.6-inch FHD, ASUS NumberPad"),
        ("MSI Titan GT77", 3200000, 4.5, "Intel Core i9-13980HX, 64GB RAM, 2TB SSD, RTX 4090, 17.3-inch 4K 144Hz"),
        ("Razer Blade 15", 2450000, 4.6, "Intel Core i9-13950HX, 32GB RAM, 1TB SSD, RTX 4080, 15.6-inch QHD 240Hz"),
        ("Huawei MateBook X Pro", 1150000, 4.4, "Intel Core i7-1360P, 16GB RAM, 1TB SSD, 14.2-inch 3.1K touchscreen, 60W USB-C"),
        ("LG Gram 16", 1250000, 4.5, "Intel Core i7-1360P, 16GB RAM, 1TB SSD, 16-inch WQXGA IPS, 1.19kg ultra-light"),
        ("Samsung Galaxy Book3 Pro", 1300000, 4.4, "Intel Core i7-1360P, 16GB RAM, 512GB SSD, 16-inch 3K AMOLED, Galaxy ecosystem"),
        ("Acer Predator Helios 300", 1200000, 4.5, "Intel Core i7-13700HX, 16GB RAM, 512GB SSD, RTX 4060, 15.6-inch QHD 165Hz"),
        ("HP Omen 16", 1350000, 4.4, "AMD Ryzen 7 7745HX, 16GB RAM, 512GB SSD, RTX 4070, 16.1-inch QHD 165Hz"),
    ],
    "Electronics": [
        ("Sony WH-1000XM5 Headphones", 450000, 4.9, "Industry-leading noise cancellation, 30hr battery, crystal clear hands-free calling, comfortable design"),
        ("Apple AirPods Pro 2nd Gen", 320000, 4.8, "Active noise cancellation, Adaptive Audio, Personalized Spatial Audio, H2 chip, USB-C"),
        ("Samsung Galaxy Buds2 Pro", 180000, 4.6, "Hi-Fi 24-bit audio, intelligent ANC, 360 audio, IPX7, 29hr total battery life"),
        ("JBL Charge 5 Bluetooth Speaker", 150000, 4.7, "IP67 waterproof, 20hr playtime, PartyBoost, built-in power bank, punchy bass"),
        ("Sony SRS-XB43 Speaker", 125000, 4.5, "Extra bass, IP67, 24hr battery, LED lighting, hands-free calling, TWS pairing"),
        ("Bose QuietComfort 45", 380000, 4.7, "Noise cancellation, Aware mode, 24hr battery, lightweight, premium audio quality"),
        ("Apple HomePod mini", 95000, 4.4, "Smart speaker, Siri, 360-degree audio, Ultra Wideband chip, smart home hub"),
        ("LG OLED 55-inch TV", 1850000, 4.8, "55-inch OLED evo, 4K 120Hz, Dolby Vision/Atmos, webOS, AI Picture Pro, G-Sync"),
        ("Samsung 65-inch QLED TV", 1650000, 4.6, "65-inch Neo QLED, 4K 120Hz, Quantum HDR 2000, Gaming Hub, SmartThings"),
        ("TCL 50-inch 4K TV", 520000, 4.3, "50-inch 4K LED, Android TV, HDR10, Dolby Audio, Google Assistant built-in"),
        ("PlayStation 5", 650000, 4.8, "Sony PS5, 825GB SSD, 4K 120fps, ray tracing, DualSense haptic feedback, backward compatible"),
        ("Xbox Series X", 620000, 4.7, "Microsoft Xbox, 1TB SSD, 4K 120fps, Quick Resume, Game Pass ready, backward compatible"),
        ("Nintendo Switch OLED", 380000, 4.7, "7-inch OLED screen, enhanced audio, 64GB storage, tabletop/TV/handheld modes"),
        ("Canon EOS R50 Mirrorless", 780000, 4.6, "24.2MP APS-C sensor, 4K 30fps video, dual-pixel AF, 15fps burst, vlogging features"),
        ("Sony Alpha A7 IV", 1850000, 4.8, "33MP full-frame BSI sensor, 4K 60fps, 759 phase-detect AF points, dual card slots"),
        ("DJI Mini 4 Pro Drone", 1200000, 4.7, "4K 100fps, 3-axis stabilization, 34min flight, OcuSync 4, Tri-Directional obstacle sensing"),
        ("GoPro Hero 12 Black", 350000, 4.5, "5.3K60 video, 27MP photos, HyperSmooth 6.0, waterproof 10m, Enduro battery"),
        ("Kindle Paperwhite 5", 85000, 4.6, "6.8-inch display, 300ppi, adjustable warm light, waterproof, 10-week battery, 32GB"),
        ("iPad Air M2", 780000, 4.7, "M2 chip, 11-inch Liquid Retina, USB-C, Apple Pencil Pro, WiFi 6E, 256GB options"),
        ("Amazon Echo Show 10", 145000, 4.3, "10.1-inch HD display, Alexa, 360-degree rotation, smart home hub, 13MP camera"),
    ],
    "Home & Kitchen": [
        ("Midea 1.5HP Split AC", 320000, 4.4, "1.5HP inverter split AC, 5-star energy rating, turbo cool, auto-clean, WiFi control"),
        ("LG 7kg Front Loader Washing Machine", 480000, 4.5, "7kg capacity, 6 motion inverter, steam wash, TurboDrum, AI DD technology"),
        ("Samsung Side-by-Side Refrigerator", 850000, 4.6, "617L capacity, All-Around cooling, Twin Cooling Plus, SpaceMax, ice maker"),
        ("Bosch Microwave Oven 25L", 125000, 4.3, "25L capacity, 900W, grill function, touch control, AutoPilot programs, stainless"),
        ("Philips Air Fryer 4.1L", 89000, 4.6, "4.1L, Rapid Air technology, 80% less fat, digital display, 7 presets, non-stick"),
        ("Nasco 43-inch Smart TV", 250000, 4.2, "43-inch FHD Smart TV, Android, built-in WiFi, Bluetooth, 2 HDMI, 2 USB ports"),
        ("Thermocool 2-Door Refrigerator", 185000, 4.1, "228L, 2-door frost-free, LED lighting, vegetable crisper, quick freeze, A+ rating"),
        ("Scanfrost Stand Mixer", 45000, 4.3, "3.5L bowl, 6-speed, dough hook/whisk/beater, tilt-head design, 250W motor"),
        ("Tiger Rice Cooker 1.8L", 38000, 4.5, "1.8L, 10-cup, tacook simultaneous cooking, non-stick inner pot, keep warm function"),
        ("Panasonic Inverter AC 1HP", 245000, 4.3, "1HP inverter, econavi, nanoe-G air purification, powerful cooling, energy-saving"),
        ("Bruhm Gas Cooker 4-Burner", 95000, 4.2, "4-burner gas cooker, tempered glass top, auto-ignition, oven with grill, 60cm"),
        ("Midea Chest Freezer 300L", 165000, 4.4, "300L chest freezer, LED lighting, lock & key, fast freeze, drain plug, A+ energy"),
        ("Dyson V15 Detect Vacuum", 650000, 4.7, "Laser dust detection, piezo sensor, 60min runtime, HEPA filtration, LCD screen"),
        ("Instant Pot Duo 7-in-1", 95000, 4.6, "6Qt, pressure cooker/slow cooker/rice cooker/steamer/sauté/yogurt/warmer"),
        ("KitchenAid Stand Mixer", 285000, 4.8, "4.8L, 10-speed, 59 touchpoints, tilt-head, 12 attachments, die-cast metal"),
        ("Nespresso Vertuo Coffee Machine", 185000, 4.5, "Centrifusion technology, 5 cup sizes, automatic capsule ejection, 40-second heat"),
        ("LG Dishwasher 14 Place", 320000, 4.3, "14 place settings, EasyRack Plus, TrueSteam, inverter motor, A+++ energy rating"),
        ("Binatone 20L Microwave", 45000, 4.1, "20L, 700W, 5 power levels, defrost, timer, child lock, easy clean interior"),
        ("Haier Thermocool 1.5HP AC", 285000, 4.2, "1.5HP split AC, UV sterilization, 5-in-1 filter, turbo cool, sleep mode, timer"),
        ("Kenwood Food Processor", 125000, 4.4, "2.1L, 1000W, stainless blades, dough attachment, julienne disc, spatula included"),
    ],
    "Fashion": [
        ("Nike Air Zoom Pegasus 40", 120000, 4.5, "Running shoe, React foam cushioning, Air Zoom unit, breathable mesh, reflective"),
        ("Adidas Ultraboost 23", 145000, 4.6, "BOOST midsole, Primeknit+ upper, Continental rubber outsole, Linear Energy Push"),
        ("Levi's 501 Original Jeans", 65000, 4.4, "Classic straight fit, 100% cotton denim, button fly, iconic back pocket stitching"),
        ("Ralph Lauren Polo Shirt", 45000, 4.3, "Classic fit polo, 100% cotton piqué, signature embroidered logo, 30+ colors"),
        ("Zara Fitted Blazer", 85000, 4.2, "Slim fit blazer, polyester-viscose blend, 2-button closure, welt pockets, lined"),
        ("Gucci GG Canvas Tote Bag", 380000, 4.7, "GG Supreme canvas, leather trim, double handles, zipper closure, dust bag"),
        ("Ray-Ban Aviator Classic", 95000, 4.6, "Crystal glass lenses, gold metal frame, UV400 protection, spring hinges, case"),
        ("Timberland 6-inch Premium Boot", 135000, 4.5, "Waterproof nubuck leather, removable ortholite footbed, rubber outsole, eco-conscious"),
        ("H&M Patterned Dress", 25000, 4.1, "Jersey fabric, regular fit, round neck, short sleeves, all-over print, knee length"),
        ("Prada Saffiano Leather Wallet", 185000, 4.5, "Saffiano leather, 8 card slots, zip coin pocket, Prada logo plaque, gift box"),
        ("Converse Chuck Taylor All Star", 55000, 4.4, "Canvas upper, OrthoLite cushioning, vulcanized rubber outsole, iconic star logo"),
        ("Balenciaga Triple S Sneaker", 650000, 4.3, "Chunky sole, mesh upper, leather overlays, Triple S branding, collector's item"),
        ("Louis Vuitton Speedy 30", 950000, 4.8, "Monogram canvas, cowhide leather trim, padlock, D-ring, luggage tag, dust bag"),
        ("Wrangler Relaxed Fit Cargo", 42000, 4.2, "Cotton-polyester blend, multiple pockets, reinforced stitching, outdoor ready"),
        ("New Balance 574 Classic", 75000, 4.4, "ENCAP midsole, suede/mesh upper, T-beam shank, classic NB logo, retro style"),
        ("Fila Disruptor 2 Platform", 68000, 4.3, "Chunky platform sole, leather upper, Fila branding, serrated rubber outsole"),
        ("Ankara Print Maxi Dress", 18000, 4.5, "100% cotton, traditional Ankara wax print, A-line silhouette, Nigerian craftsmanship"),
        ("Agbada Traditional Suit", 85000, 4.6, "Embroidered Agbada set, 3-piece, Aso-oke fabric, traditional Nigerian formal wear"),
        ("Senator Native Wear Set", 35000, 4.4, "Cotton senator fabric, embroidered details, 2-piece set, Nigerian menswear"),
        ("Fascia Isiagu Shirt", 28000, 4.3, "Isiagu traditional fabric, lion head pattern, 100% cotton, Igbo formal attire"),
    ],
    "Books": [
        ("Atomic Habits by James Clear", 8500, 4.8, "Tiny changes, remarkable results. Build good habits, break bad ones, master the system"),
        ("Rich Dad Poor Dad by Kiyosaki", 7500, 4.7, "Financial literacy, asset vs liability, investing mindset, passive income strategies"),
        ("Things Fall Apart by Chinua Achebe", 5000, 4.9, "Nigerian literary masterpiece, Okonkwo's story, Igbo culture, colonial impact"),
        ("The Psychology of Money", 8000, 4.7, "Morgan Housel on wealth, greed, happiness, and timeless lessons about money behavior"),
        ("Purple Hibiscus by Chimamanda Adichie", 5500, 4.8, "Coming-of-age novel, family dynamics, Nigerian politics, freedom, faith and freedom"),
        ("Think and Grow Rich", 6500, 4.6, "Napoleon Hill's classic, 13 principles of success, mindset, desire, persistence"),
        ("Half of a Yellow Sun", 6500, 4.8, "Chimamanda's Biafra war novel, love, loss, identity, and the Nigeria-Biafra conflict"),
        ("The Lean Startup", 9000, 4.5, "Eric Ries on building startups, validated learning, MVP, pivot or persevere methodology"),
        ("Deep Work by Cal Newport", 8500, 4.7, "Rules for focused success in a distracted world, intense concentration, flow state"),
        ("Becoming by Michelle Obama", 9500, 4.8, "Former First Lady's memoir, Chicago roots, Princeton, Harvard Law, White House life"),
        ("The 48 Laws of Power", 8500, 4.5, "Robert Greene's guide to power dynamics, historical examples, strategy and manipulation"),
        ("Zero to One by Peter Thiel", 9000, 4.6, "Notes on startups, building the future, monopoly, secrets, foundations of companies"),
        ("Man's Search for Meaning", 7000, 4.9, "Viktor Frankl's Holocaust memoir, logotherapy, finding meaning in suffering"),
        ("Sapiens by Yuval Noah Harari", 9500, 4.7, "Brief history of humankind, cognitive revolution, agricultural, scientific, future"),
        ("The Alchemist by Paulo Coelho", 7500, 4.7, "Personal legend, following your dreams, the universe conspiring in your favor"),
        ("WAEC Mathematics Textbook", 3500, 4.3, "Comprehensive WAEC prep, all topics, past questions, worked examples, revision"),
        ("JAMB CBT Practice Questions", 2500, 4.4, "All subjects, 10,000+ questions, answer explanations, exam-ready preparation"),
        ("Nigerian Law and Practice", 12000, 4.5, "Comprehensive Nigerian law textbook, constitutional law, criminal law, civil procedure"),
        ("Introduction to Python Programming", 8500, 4.6, "Beginner to advanced Python, OOP, data structures, algorithms, projects included"),
        ("Financial Accounting ICAN Study Pack", 9500, 4.5, "ICAN exam prep, all chapters, past questions, worked solutions, exam tips"),
    ],
    "Gaming": [
        ("PlayStation 5 DualSense Controller", 95000, 4.8, "Haptic feedback, adaptive triggers, USB-C, built-in mic, speaker, 12hr battery"),
        ("Xbox Elite Wireless Controller", 125000, 4.7, "Pro-level, adjustable tension thumbsticks, wrap-around rubberized grip, Bluetooth"),
        ("Razer DeathAdder V3 Pro Mouse", 85000, 4.6, "Focus Pro 30K sensor, 90hr battery, HyperSpeed wireless, 5 programmable buttons"),
        ("Corsair K70 RGB Mechanical Keyboard", 95000, 4.5, "Cherry MX switches, per-key RGB, aircraft-grade aluminum frame, media controls"),
        ("SteelSeries Arctis Nova 7 Headset", 125000, 4.6, "Dual wireless, ANC, 38hr battery, ClearCast Gen 2 mic, ChatMix dial, USB-C"),
        ("ASUS ROG 27-inch Gaming Monitor", 385000, 4.7, "27-inch 2K 170Hz IPS, 1ms GTG, ELMB Sync, FreeSync Premium Pro, HDR400"),
        ("Logitech G Pro X Superlight 2", 95000, 4.7, "HERO 25K sensor, 63g weight, HyperSpeed wireless, PTFE feet, 70hr battery"),
        ("MSI Optix MAG271CQR Monitor", 285000, 4.4, "27-inch 1440p curved, 165Hz, 1ms, AMD FreeSync Premium, Night Vision"),
        ("Nintendo Switch Pro Controller", 65000, 4.6, "HD rumble, amiibo, NFC reader, gyro-axis, Bluetooth, 40hr battery"),
        ("Razer Kraken V3 HyperSense", 78000, 4.4, "Haptic technology, THX spatial audio, HyperClear cardioid mic, RGB, USB"),
        ("Gaming Chair by DXRacer", 185000, 4.5, "Ergonomic design, lumbar support, neck pillow, 90-135° recline, 4D armrests"),
        ("Elgato Stream Deck MK.2", 95000, 4.7, "15 LCD keys, customizable actions, plugins, stream/YouTube/Twitch integration"),
        ("Capture Card Elgato HD60 X", 125000, 4.5, "4K30/1080p60 capture, ultra-low latency, VRR, instant gameview, USB 3.0"),
        ("WD_BLACK 2TB SN850X NVMe SSD", 95000, 4.7, "7300MB/s read, PS5/PC optimized, PCIe Gen4, M.2 2280, game mode 2.0"),
        ("Seagate Firecuda 4TB HDD", 45000, 4.3, "7200RPM, 256MB cache, SATA 6Gb/s, rescue data services, gaming storage"),
        ("Astro A50 Wireless Headset", 185000, 4.5, "Dolby Audio, ASTRO Audio V2, mod kit, base station, 15hr battery, PS5/PC"),
        ("HyperX Cloud II Gaming Headset", 65000, 4.5, "53mm drivers, virtual 7.1 surround, detachable mic, memory foam, USB/3.5mm"),
        ("Turtle Beach Recon Controller", 45000, 4.2, "Superhuman Hearing, 3.5mm audio, ProAim sensitivity settings, Xbox/PC"),
        ("Thrustmaster T300RS Wheel", 285000, 4.6, "Brushless motor, force feedback, 270°-1080°, PS5/PS4/PC, T3PA pedals"),
        ("Razer Basilisk V3 Pro Mouse", 95000, 4.6, "HyperScroll Tilt Wheel, Focus Pro 30K, Chroma RGB, 11 programmable buttons"),
    ],
}

PRODUCT_IMAGES = {
    "Smartphones": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
    "Laptops": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
    "Electronics": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
    "Home & Kitchen": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
    "Fashion": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=400",
    "Books": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",
    "Gaming": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=400",
}

CATEGORY_IMAGES = {
    "Smartphones": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=300",
    "Laptops": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300",
    "Electronics": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300",
    "Home & Kitchen": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300",
    "Fashion": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=300",
    "Books": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300",
    "Gaming": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=300",
}

NIGERIAN_NAMES = [
    "Oluwa Victor", "Chidi Okafor", "Amaka Eze", "Emeka Nwosu", "Ngozi Adeyemi",
    "Tunde Bakare", "Chioma Obi", "Seun Afolabi", "Ifeanyi Madu", "Yetunde Lawal",
    "Obinna Igwe", "Blessing Uchenna", "Rotimi Adewale", "Adaeze Onwudiwe", "Babajide Akinwale",
    "Kelechi Onyeka", "Sade Ogundimu", "Uche Nzekwe", "Toyin Fashola", "Olumide Adebayo",
    "Chiamaka Eze", "Damilola Adesanya", "Nnamdi Okeke", "Funmi Adeleke", "Gbenga Olatunde",
    "Nneka Chukwu", "Taiwo Ogundele", "Chinonso Obi", "Kehinde Adeleke", "Olamide Ibidun",
]


def generate_products():
    """Generate 2000+ products with realistic data"""
    products = []
    pid = 1
    
    for category, items in PRODUCTS_DATA.items():
        for name, base_price, base_rating, description in items:
            # Original product
            img_base = PRODUCT_IMAGES[category]
            products.append({
                "product_id": pid,
                "name": name,
                "category": category,
                "price": base_price,
                "description": description,
                "rating": base_rating,
                "num_reviews": random.randint(15, 350),
                "image_url": img_base,
                "in_stock": random.random() > 0.1,
                "tags": f"{category.lower()},{name.lower().split()[0]},{description.split(',')[0].lower()}",
                "brand": name.split()[0],
                "views": random.randint(100, 5000),
                "purchases": random.randint(10, 500),
            })
            pid += 1
    
    # Expand to 2000+ by creating variants
    base_products = products.copy()
    multipliers = [
        ("- Pro Version", 1.3, 0.1),
        ("- Lite Edition", 0.75, -0.1),
        ("- Bundle Pack", 1.5, 0.05),
        ("- Special Edition", 1.2, 0.05),
        ("- Refurbished", 0.65, -0.2),
        ("(Black)", 1.0, 0.0),
        ("(White)", 1.0, 0.0),
        ("(Space Gray)", 1.0, 0.0),
        ("(Rose Gold)", 1.05, 0.0),
        ("(Navy Blue)", 1.0, 0.0),
    ]
    
    for p in base_products:
        for suffix, price_mult, rating_delta in multipliers:
            new_price = int(p["price"] * price_mult)
            new_rating = round(min(5.0, max(1.0, p["rating"] + rating_delta + random.uniform(-0.1, 0.1))), 1)
            products.append({
                "product_id": pid,
                "name": f"{p['name']} {suffix}",
                "category": p["category"],
                "price": new_price,
                "description": p["description"] + f". {suffix.strip('- ').strip('()')} variant with enhanced features.",
                "rating": new_rating,
                "num_reviews": random.randint(5, 200),
                "image_url": p["image_url"],
                "in_stock": random.random() > 0.15,
                "tags": p["tags"],
                "brand": p["brand"],
                "views": random.randint(50, 2000),
                "purchases": random.randint(5, 200),
            })
            pid += 1
            if pid > 2200:
                break
        if pid > 2200:
            break
    
    return pd.DataFrame(products)


def generate_users(n=5000):
    """Generate 5000+ realistic Nigerian users"""
    users = []
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    
    for i in range(1, n + 1):
        name = random.choice(NIGERIAN_NAMES) + f" {random.randint(1, 999)}"
        clean_name = name.lower().replace(" ", ".")
        users.append({
            "user_id": i,
            "name": name,
            "email": f"{clean_name}@{random.choice(domains)}",
            "age": random.randint(18, 55),
            "city": random.choice(["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Kano", "Enugu", "Benin City", "Warri"]),
            "date_joined": (datetime.now() - timedelta(days=random.randint(1, 730))).isoformat(),
            "preferred_categories": json.dumps(random.sample(list(PRODUCTS_DATA.keys()), k=random.randint(1, 3))),
        })
    return pd.DataFrame(users)


def generate_ratings(products_df, users_df, n=10000):
    """Generate 10000+ ratings"""
    ratings = []
    product_ids = products_df["product_id"].tolist()
    user_ids = users_df["user_id"].tolist()
    
    for i in range(1, n + 1):
        pid = random.choice(product_ids)
        uid = random.choice(user_ids)
        base = products_df[products_df["product_id"] == pid]["rating"].values[0]
        rating = round(min(5.0, max(1.0, base + random.uniform(-1.5, 1.5))), 1)
        ratings.append({
            "rating_id": i,
            "user_id": uid,
            "product_id": pid,
            "rating": rating,
            "review": f"Good product overall. {'Highly recommend.' if rating > 3.5 else 'Decent value.'}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
        })
    return pd.DataFrame(ratings)


def generate_activities(products_df, users_df, n=50000):
    """Generate 50000+ user activity interactions"""
    activities = []
    product_ids = products_df["product_id"].tolist()
    user_ids = users_df["user_id"].tolist()
    actions = ["view", "click", "like", "wishlist", "purchase"]
    action_weights = [0.45, 0.25, 0.12, 0.10, 0.08]
    
    for i in range(1, n + 1):
        activities.append({
            "activity_id": i,
            "user_id": random.choice(user_ids),
            "product_id": random.choice(product_ids),
            "action": random.choices(actions, weights=action_weights)[0],
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))).isoformat(),
        })
    return pd.DataFrame(activities)


def init_database(db_path):
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT, email TEXT UNIQUE, age INTEGER,
        city TEXT, date_joined TEXT, preferred_categories TEXT,
        password TEXT DEFAULT 'hashed_password'
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT, category TEXT, price REAL,
        description TEXT, rating REAL, num_reviews INTEGER,
        image_url TEXT, in_stock INTEGER, tags TEXT,
        brand TEXT, views INTEGER, purchases INTEGER
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS ratings (
        rating_id INTEGER PRIMARY KEY,
        user_id INTEGER, product_id INTEGER,
        rating REAL, review TEXT, timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS user_activity (
        activity_id INTEGER PRIMARY KEY,
        user_id INTEGER, product_id INTEGER,
        action TEXT, timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )""")
    
    conn.commit()
    return conn


def generate_all_data(data_dir, db_path):
    """Generate and save all data"""
    print("Generating products...")
    products_df = generate_products()
    products_df.to_csv(f"{data_dir}/products.csv", index=False)
    print(f"  → {len(products_df)} products generated")

    print("Generating users...")
    users_df = generate_users(5000)
    users_df.to_csv(f"{data_dir}/users.csv", index=False)
    print(f"  → {len(users_df)} users generated")

    print("Generating ratings...")
    ratings_df = generate_ratings(products_df, users_df, 10000)
    ratings_df.to_csv(f"{data_dir}/ratings.csv", index=False)
    print(f"  → {len(ratings_df)} ratings generated")

    print("Generating activities (this may take a moment)...")
    activities_df = generate_activities(products_df, users_df, 50000)
    activities_df.to_csv(f"{data_dir}/activities.csv", index=False)
    print(f"  → {len(activities_df)} activities generated")

    print("Saving category images config...")
    with open(f"{data_dir}/category_images.json", "w") as f:
        json.dump(CATEGORY_IMAGES, f)

    print("Initializing database...")
    conn = init_database(db_path)
    
    products_df.to_sql("products", conn, if_exists="replace", index=False)
    users_df.to_sql("users", conn, if_exists="replace", index=False)
    ratings_df.to_sql("ratings", conn, if_exists="replace", index=False)
    activities_df.to_sql("user_activity", conn, if_exists="replace", index=False)
    conn.close()
    print("Database initialized successfully!")
    
    return products_df, users_df, ratings_df, activities_df


if __name__ == "__main__":
    import os
    data_dir = "data"
    db_path = "database/database.db"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs("database", exist_ok=True)
    generate_all_data(data_dir, db_path)
    print("\n✅ All data generated successfully!")
