from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Category, Product


class EcommerceProductTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testadmin', password='password123')
        self.client = Client()

        # Create category
        self.category = Category.objects.create(name='Clothing')
        self.category2 = Category.objects.create(name='Electronics')

        # Create products
        self.product1 = Product.objects.create(
            name='T-Shirt',
            sku='TSHIRT-001',
            category=self.category,
            price=Decimal('999.00'),
            stock=15,
            status='Active'
        )
        self.product2 = Product.objects.create(
            name='Jeans',
            sku='JEANS-001',
            category=self.category,
            price=Decimal('1500.00'),
            stock=4,  # Low stock <= 5
            status='Active'
        )
        self.product3 = Product.objects.create(
            name='Earphones',
            sku='EAR-001',
            category=self.category2,
            price=Decimal('499.00'),
            stock=1,  # Low stock <= 5
            status='Inactive'
        )

    def test_login_flow(self):
        # Attempt login with correct credentials
        response = self.client.post(reverse('login'), {
            'username': 'testadmin',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('dashboard'))

        # Check authenticated session
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_metrics(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_products'], 3)
        self.assertEqual(response.context['active_products'], 2)
        self.assertEqual(response.context['inactive_products'], 1)
        self.assertEqual(response.context['low_stock_products'], 2)

    def test_product_list_search_and_filter(self):
        self.client.login(username='testadmin', password='password123')

        # Search by name
        response = self.client.get(reverse('product_list'), {'search': 'T-Shirt'})
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].name, 'T-Shirt')

        # Filter by category
        response = self.client.get(reverse('product_list'), {'category': self.category2.id})
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].name, 'Earphones')

        # Filter by status
        response = self.client.get(reverse('product_list'), {'status': 'Inactive'})
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].name, 'Earphones')

    def test_product_creation_and_validation(self):
        self.client.login(username='testadmin', password='password123')

        # Successful creation
        response = self.client.post(reverse('product_add'), {
            'name': 'Formal Shirt',
            'sku': 'SHIRT-001',
            'category': self.category.id,
            'price': '799.00',
            'stock': '10',
            'status': 'Active',
            'description': 'Pure cotton formal shirt.'
        })
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(sku='SHIRT-001').exists())

        # Validation: Duplicate SKU
        response = self.client.post(reverse('product_add'), {
            'name': 'Duplicate Shirt',
            'sku': 'SHIRT-001',
            'category': self.category.id,
            'price': '799.00',
            'stock': '10',
            'status': 'Active'
        })
        self.assertFormError(response.context['form'], 'sku', 'A product with this SKU already exists.')

        # Validation: Price <= 0
        response = self.client.post(reverse('product_add'), {
            'name': 'Zero Price Item',
            'sku': 'ZERO-001',
            'category': self.category.id,
            'price': '0.00',
            'stock': '10',
            'status': 'Active'
        })
        self.assertFormError(response.context['form'], 'price', 'Price must be greater than 0.')

        # Validation: Stock < 0
        response = self.client.post(reverse('product_add'), {
            'name': 'Negative Stock Item',
            'sku': 'NEG-001',
            'category': self.category.id,
            'price': '100.00',
            'stock': '-5',
            'status': 'Active'
        })
        self.assertFormError(response.context['form'], 'stock', 'Stock cannot be negative.')

    def test_product_update(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.post(reverse('product_edit', args=[self.product1.pk]), {
            'name': 'Classic T-Shirt Updated',
            'sku': 'TSHIRT-001',
            'category': self.category.id,
            'price': '1099.00',
            'stock': '20',
            'status': 'Active',
            'description': 'Updated description.'
        })
        self.assertRedirects(response, reverse('product_list'))
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Classic T-Shirt Updated')
        self.assertEqual(self.product1.price, Decimal('1099.00'))
        self.assertEqual(self.product1.stock, 20)

    def test_product_delete(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.post(reverse('product_delete', args=[self.product1.pk]))
        self.assertRedirects(response, reverse('product_list'))
        self.assertFalse(Product.objects.filter(pk=self.product1.pk).exists())

    def test_unauthenticated_access_restricted(self):
        # Unauthenticated user cannot access dashboard or CRUD
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        response = self.client.get(reverse('product_add'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dummyjson_sync(self):
        import unittest.mock as mock
        import json

        fake_api_response = json.dumps({
            "products": [
                {
                    "id": 999,
                    "title": "API Wireless Headphones",
                    "sku": "API-HEAD-999",
                    "category": "audio",
                    "price": 149.99,
                    "stock": 8,
                    "description": "Noise cancelling headphones.",
                    "thumbnail": "https://example.com/headphones.jpg"
                }
            ]
        }).encode()

        self.client.login(username='testadmin', password='password123')
        
        with mock.patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = mock.MagicMock()
            mock_cm.read.return_value = fake_api_response
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            response = self.client.get(reverse('sync_dummyjson'))
            self.assertRedirects(response, reverse('product_list'))

        synced_prod = Product.objects.get(sku='API-HEAD-999')
        self.assertEqual(synced_prod.name, 'API Wireless Headphones')
        self.assertEqual(synced_prod.category.name, 'Audio')
        self.assertEqual(synced_prod.price, Decimal('149.99'))
        self.assertEqual(synced_prod.stock, 8)
        self.assertEqual(synced_prod.image_url, 'https://example.com/headphones.jpg')
