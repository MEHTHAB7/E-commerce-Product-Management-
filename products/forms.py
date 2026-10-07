from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'price', 'stock', 'image', 'description', 'status']
        labels = {
            'name': 'Product Name',
            'sku': 'SKU',
            'category': 'Category',
            'price': 'Price (₹)',
            'stock': 'Stock Quantity',
            'image': 'Product Image',
            'description': 'Description',
            'status': 'Status',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Classic Cotton T-Shirt'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TSHIRT-001'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '999.00'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '15'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Product description...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("Product name is required.")
        return name.strip()

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if not sku or not sku.strip():
            raise forms.ValidationError("SKU is required.")
        sku = sku.strip()
        # Check uniqueness excluding self when updating
        qs = Product.objects.filter(sku__iexact=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A product with this SKU already exists.")
        return sku

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Price is required.")
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError("Stock quantity is required.")
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category is required.")
        return category
