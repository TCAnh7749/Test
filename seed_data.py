import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KTHP.settings')
django.setup()

from home.models import Category, Product

# Create Categories
phone_cat, _ = Category.objects.get_or_create(
    name='Điện thoại', 
    slug='dien-thoai', 
    defaults={'description': 'Điện thoại thông minh xuất sắc nhất.'}
)

laptop_cat, _ = Category.objects.get_or_create(
    name='Laptop', 
    slug='laptop', 
    defaults={'description': 'Máy tính xách tay cấu hình cao.'}
)

accessory_cat, _ = Category.objects.get_or_create(
    name='Phụ kiện', 
    slug='phu-kien', 
    defaults={'description': 'Phụ kiện công nghệ chính hãng.'}
)

# Create Products
products_data = [
    {
        'category': phone_cat,
        'name': 'iPhone 15 Pro Max',
        'slug': 'iphone-15-pro-max',
        'description': 'Siêu phẩm Apple mới nhất với thiết kế Titan nguyên khối, camera 48MP và chip A17 Pro siêu mạnh.',
        'price': '1199.00',
        'stock': 50,
        'screen_size': '6.7 inch Super Retina XDR',
        'cpu': 'Apple A17 Pro 6 nhân',
        'ram': '8 GB',
        'storage': '256 GB',
    },
    {
        'category': phone_cat,
        'name': 'Samsung Galaxy S24 Ultra',
        'slug': 'samsung-galaxy-s24-ultra',
        'description': 'Điện thoại AI đột phá, khung viền Titan và tích hợp bút S-Pen. Màn hình phẳng chống lóa xuất sắc.',
        'price': '1299.00',
        'stock': 30,
        'screen_size': '6.8 inch Dynamic AMOLED 2X',
        'cpu': 'Snapdragon 8 Gen 3 for Galaxy',
        'ram': '12 GB',
        'storage': '512 GB',
    },
    {
        'category': laptop_cat,
        'name': 'MacBook Pro 16 inch M3 Max',
        'slug': 'macbook-pro-16-m3-max',
        'description': 'Chiếc laptop mạnh mẽ nhất dành cho giới chuyên nghiệp với chip M3 Max khủng khiếp và thời lượng pin đỉnh cao.',
        'price': '3499.00',
        'stock': 15,
        'screen_size': '16.2 inch Liquid Retina XDR',
        'cpu': 'Apple M3 Max 16-core CPU',
        'ram': '48 GB Unified Memory',
        'storage': '1 TB SSD',
    },
    {
        'category': laptop_cat,
        'name': 'Asus ROG Zephyrus G14',
        'slug': 'asus-rog-zephyrus-g14',
        'description': 'Laptop gaming nhỏ gọn 14 inch mạnh mẽ nhất thế giới với thiết kế nhôm CNC sang trọng.',
        'price': '1599.00',
        'stock': 20,
        'screen_size': '14 inch OLED 3K 120Hz',
        'cpu': 'AMD Ryzen 9 8945HS',
        'ram': '32 GB LPDDR5X',
        'storage': '1 TB SSD',
    },
    {
        'category': accessory_cat,
        'name': 'AirPods Pro 2 (USB-C)',
        'slug': 'airpods-pro-2-usb-c',
        'description': 'Tai nghe chống ồn chủ động xuất sắc bản nâng cấp USB-C, âm thanh không gian đột phá.',
        'price': '249.00',
        'stock': 100,
        'screen_size': '',
        'cpu': 'Apple H2',
        'ram': '',
        'storage': '',
    }
]

for pdata in products_data:
    Product.objects.get_or_create(
        slug=pdata['slug'],
        defaults=pdata
    )

print("Đã thêm thành công 3 danh mục và 5 sản phẩm!")
