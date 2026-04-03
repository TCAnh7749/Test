from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Category, Product, Order, OrderItem
from .cart import Cart

def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)[:12]
    return render(request, 'store/index.html', {'categories': categories, 'products': products})

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
        
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product_list.html', {'category': category, 'categories': categories, 'products': products, 'query': query})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/detail.html', {'product': product})

# --- Cart Views ---
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # Simple form submission for quantity
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'cart_count': len(cart)})
        
    return redirect('home:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('home:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('home:cart_detail')

# --- Checkout Views ---
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        # Create order
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        payment_method = request.POST.get('payment_method', 'cash')

        order = Order.objects.create(
            first_name=first_name, last_name=last_name, 
            email=email, address=address, 
            postal_code=postal_code, city=city,
            payment_method=payment_method
        )
        if request.user.is_authenticated:
            order.user = request.user
            order.save()
            
        for item in cart:
            OrderItem.objects.create(
                order=order, product=item['product'],
                price=item['price'], quantity=item['quantity']
            )
        cart.clear()
        return render(request, 'store/order_created.html')
    return render(request, 'store/checkout.html', {'cart': cart})

# --- Authentication Views ---
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home:home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home:home')
            if next_url == '/': next_url = 'home:home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home:home')

# --- Error Views ---
def error(request, exception=None):
    return render(request, 'error.html', status=404)

def error_500(request):
    return render(request, 'error.html', status=500)

