from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductForm


def login_view(request):
    """Simple login view with basic validation."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'products/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'products/login.html')


def logout_view(request):
    """Logs out user and redirects to login page."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Dashboard overview showing simple cards:
    - Total Products
    - Active Products
    - Inactive Products
    - Low Stock Products (stock <= 5)
    """
    total_products = Product.objects.count()
    active_products = Product.objects.filter(status='Active').count()
    inactive_products = Product.objects.filter(status='Inactive').count()
    low_stock_products = Product.objects.filter(stock__lte=5).count()

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'inactive_products': inactive_products,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'products/dashboard.html', context)


@login_required
def product_list_view(request):
    """
    Product list page with search, filters (category, active/inactive),
    and pagination.
    """
    queryset = Product.objects.select_related('category').all()

    # Search by product name
    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Filter by status (Active / Inactive)
    status_filter = request.GET.get('status', '')
    if status_filter in ['Active', 'Inactive']:
        queryset = queryset.filter(status=status_filter)

    # Basic pagination (10 per page)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status_filter,
    }
    return render(request, 'products/product_list.html', context)


@login_required
def product_create_view(request):
    """Create a new product using ProductForm."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" was successfully added.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Add Product',
        'is_edit': False,
    })


@login_required
def product_update_view(request, pk):
    """Edit an existing product using the same ProductForm."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" was successfully updated.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product',
        'is_edit': True,
    })


@login_required
def product_delete_view(request, pk):
    """Delete a product with confirmation."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" was successfully deleted.')
        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {
        'product': product,
    })


@login_required
def product_detail_view(request, pk):
    """View single product details."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def sync_dummyjson_view(request):
    """Fetches and syncs products from DummyJSON API."""
    import json
    import urllib.request
    from decimal import Decimal

    url = 'https://dummyjson.com/products?limit=30'
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            products_list = data.get('products', [])

        count = 0
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
            status = 'Inactive' if stock == 0 else 'Active'

            Product.objects.update_or_create(
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
            count += 1

        messages.success(request, f'Successfully synced {count} products from DummyJSON API!')
    except Exception as e:
        messages.error(request, f'Failed to sync products from DummyJSON API: {e}')

    return redirect('product_list')
