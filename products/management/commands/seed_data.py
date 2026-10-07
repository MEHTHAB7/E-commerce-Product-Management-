import json
import urllib.request
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Fetches products from DummyJSON API and seeds the database'

    def handle(self, *args, **kwargs):
        # 1. Create Default Admin User
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created with password "{password}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists.'))

        # 2. Fetch live products from DummyJSON API
        url = 'https://dummyjson.com/products?limit=30'
        self.stdout.write(f'Fetching products from {url}...')

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                products_list = data.get('products', [])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch from DummyJSON API: {e}'))
            return

        # 3. Save products to database
        created_count = 0
        updated_count = 0

        for item in products_list:
            raw_category = item.get('category', 'General')
            category_name = raw_category.replace('-', ' ').title()
            category, _ = Category.objects.get_or_create(name=category_name)

            sku = item.get('sku') or f"SKU-{item.get('id')}"
            name = item.get('title')
            price = Decimal(str(item.get('price', '1.00')))
            stock = int(item.get('stock', 0))
            description = item.get('description', '')
            image_url = item.get('thumbnail') or (item.get('images', [None])[0] if item.get('images') else None)
            
            # If stock is 0, mark Inactive, otherwise Active
            status = 'Inactive' if stock == 0 else 'Active'

            product, created = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': category,
                    'price': price,
                    'stock': stock,
                    'description': description,
                    'image_url': image_url,
                    'status': status,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {len(products_list)} products from DummyJSON API '
            f'({created_count} created, {updated_count} updated).'
        ))
