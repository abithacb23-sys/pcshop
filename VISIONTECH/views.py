from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import models
from .models import Category, Product, Brand, Order, OrderItem, UserProfile, SupportTicket
from .forms import BrandForm, ProductForm
import json
import random
from decimal import Decimal

def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_featured=True)[:6]
    trending_products = Product.objects.all()[:3]
    return render(request, 'index.html', {
        'categories': categories,
        'featured_products': featured_products,
        'trending_products': trending_products
    })

def catalog(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    sort_by = request.GET.get('sort', 'name') # name, price_asc, price_desc

    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    active_brand = None
    if brand_slug:
        active_brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=active_brand)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    return render(request, 'catalog.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'active_category': active_category,
        'active_brand': active_brand,
        'query': query,
        'sort_by': sort_by
    })


def brand_list(request):
    brands = list(Brand.objects.all().order_by('name'))
    brand_fallback = False

    if not brands:
        product_brands = Product.objects.filter(brand__isnull=False).values('brand__name', 'brand__slug').distinct()
        if product_brands:
            brands = [
                {
                    'name': pb['brand__name'],
                    'slug': pb['brand__slug'],
                    'website': '',
                    'logo_url': ''
                }
                for pb in product_brands
            ]
            brand_fallback = True

    return render(request, 'brand_list.html', {
        'brands': brands,
        'brand_fallback': brand_fallback
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def pc_builder(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Pack products as category lists for template/JS integration
    builder_data = {}
    for cat in categories:
        builder_data[cat.slug] = products.filter(category=cat)

    return render(request, 'pc_builder.html', {
        'builder_data': builder_data,
        'categories': categories
    })

def get_cart(request):
    cart = request.session.get('cart', {})
    # Verify cart structure, clean up if needed
    if not isinstance(cart, dict):
        cart = {}
    return cart

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def cart_view(request):
    cart = get_cart(request)
    cart_items = []
    subtotal = Decimal('0.00')
    total_weight = Decimal('0.00')

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            quantity = item_data.get('quantity', 1)
            total = product.price * quantity
            subtotal += total
            
            # calculate weight
            item_weight = Decimal(str(product.weight)) * quantity
            total_weight += item_weight
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': total,
                'item_weight': item_weight,
                'overclock': item_data.get('overclock', False),
                'rgb_color': item_data.get('rgb_color', 'Default')
            })
        except Product.DoesNotExist:
            continue

    tax = subtotal * Decimal('0.18')  # 18% tax
    grand_total = subtotal + tax

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'total_weight': total_weight
    })

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    
    quantity = int(request.GET.get('quantity', 1))
    overclock = request.GET.get('overclock', 'false') == 'true'
    rgb_color = request.GET.get('rgb_color', 'Default')
    
    # Stock validation
    pid_str = str(product_id)
    existing_qty = cart.get(pid_str, {}).get('quantity', 0)
    total_requested = existing_qty + quantity
    
    if total_requested > product.stock:
        messages.error(request, f"Cannot add {quantity} units of {product.name}. Available stock is {product.stock} units.")
        return redirect('product_detail', slug=product.slug)
    
    if pid_str in cart:
        cart[pid_str]['quantity'] = total_requested
    else:
        cart[pid_str] = {
            'quantity': quantity,
            'overclock': overclock,
            'rgb_color': rgb_color
        }
    
    save_cart(request, cart)
    return redirect('cart_view')

@require_POST
def cart_update(request, product_id):
    cart = get_cart(request)
    pid_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        if quantity > 0:
            if quantity > product.stock:
                return JsonResponse({'status': 'error', 'message': f"Available stock is {product.stock} units."}, status=400)
            if pid_str in cart:
                cart[pid_str]['quantity'] = quantity
                save_cart(request, cart)
                return JsonResponse({'status': 'success'})
        else:
            if pid_str in cart:
                del cart[pid_str]
                save_cart(request, cart)
                return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid input'}, status=400)

def cart_remove(request, product_id):
    cart = get_cart(request)
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        save_cart(request, cart)
    return redirect('cart_view')

@require_POST
def cart_add_custom_rig(request):
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        cart = get_cart(request)
        
        for pid in product_ids:
            if not pid:
                continue
            pid_str = str(pid)
            if pid_str in cart:
                cart[pid_str]['quantity'] += 1
            else:
                cart[pid_str] = {
                    'quantity': 1,
                    'overclock': False,
                    'rgb_color': 'Custom Build Aura'
                }
                
        save_cart(request, cart)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('catalog')

    # Calculate totals
    subtotal = Decimal('0.00')
    cart_items = []
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            quantity = item_data.get('quantity', 1)
            total = product.price * quantity
            subtotal += total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': total
            })
        except Product.DoesNotExist:
            continue

    tax = subtotal * Decimal('0.18')
    grand_total = subtotal + tax

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')

        # Calculate total weight
        total_weight = Decimal('0.00')
        for item in cart_items:
            total_weight += Decimal(str(item['product'].weight)) * item['quantity']

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            zip_code=zip_code,
            total_price=grand_total,
            weight=total_weight
        )

        # Save order items and decrement stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
            # Decrement inventory stock
            product = item['product']
            product.stock = max(0, product.stock - item['quantity'])
            product.save()

        # Keep order IDs in session to display in dashboard
        my_orders = request.session.get('my_orders', [])
        my_orders.append(order.id)
        request.session['my_orders'] = my_orders
        request.session.modified = True

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'checkout_success.html', {'order': order})

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total
    })

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Sync guest orders from session to logged-in user
    session_orders = request.session.get('my_orders', [])
    if session_orders:
        Order.objects.filter(id__in=session_orders, user__isnull=True).update(user=request.user)
        request.session['my_orders'] = []
        request.session.modified = True
        
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate average rig rating or tier
    order_count = orders.count()
    if order_count >= 5:
        gamer_tier = "Legendary Overclocker"
        tier_color = "#ff0055"
    elif order_count >= 2:
        gamer_tier = "Elite Builder"
        tier_color = "#7b2ff7"
    elif order_count == 1:
        gamer_tier = "PC Enthusiast"
        tier_color = "#00cfff"
    else:
        gamer_tier = "Novice Cadet"
        tier_color = "#888888"

    if request.method == 'POST':
        # Profile updates
        profile.shipping_address = request.POST.get('shipping_address', '')
        profile.phone = request.POST.get('phone', '')
        profile.avatar = request.POST.get('avatar', 'bi-person-workspace')
        profile.save()
        
        # update user's email if changed
        email = request.POST.get('email', '')
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()
            
        messages.success(request, "Operator profile credentials updated in database.")
        return redirect('dashboard')

    return render(request, 'dashboard.html', {
        'orders': orders,
        'tickets': tickets,
        'profile': profile,
        'gamer_tier': gamer_tier,
        'tier_color': tier_color,
        'order_count': order_count
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        shipping_address = request.POST.get('shipping_address', '')
        phone = request.POST.get('phone', '')
        avatar = request.POST.get('avatar', 'bi-person-workspace')
        
        if not username or not email or not password:
            messages.error(request, "All core node registration fields are required.")
            return render(request, 'register.html')
            
        if password != confirm_password:
            messages.error(request, "Security keys mismatch. Confirm password correctly.")
            return render(request, 'register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Operator username is already registered.")
            return render(request, 'register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email coordinates are already registered.")
            return render(request, 'register.html')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        # Create user profile
        UserProfile.objects.create(
            user=user,
            shipping_address=shipping_address,
            phone=phone,
            avatar=avatar
        )
        
        messages.success(request, "Registration successful! Propose authentication details below.")
        return redirect('login_view')

    return render(request, 'register.html')


@staff_member_required
def admin_panel(request):
    brands = Brand.objects.all()
    products = Product.objects.select_related('brand', 'category').all()[:200]
    return render(request, 'admin_panel.html', {
        'brands': brands,
        'products': products,
    })


@staff_member_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = BrandForm()
    return render(request, 'brand_form.html', {'form': form, 'title': 'Create Brand'})


@staff_member_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'brand_form.html', {'form': form, 'title': 'Edit Brand'})


@staff_member_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        return redirect('admin_panel')
    return render(request, 'brand_confirm_delete.html', {'brand': brand})


@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'title': 'Create Product'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Generate a random 6-digit passcode for simulation
            mfa_code = str(random.randint(100000, 999999))
            request.session['pre_mfa_user_id'] = user.id
            request.session['mfa_code'] = mfa_code
            return redirect('mfa_verify_view')
        else:
            messages.error(request, "Invalid security credentials.")
            
    return render(request, 'login.html')

def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_panel')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            auth_login(request, user)
            messages.success(request, f"Welcome administrator {user.username}.")
            return redirect('admin_panel')
        elif user is not None:
            messages.error(request, "This account does not have admin access.")
        else:
            messages.error(request, "Invalid admin credentials.")

    return render(request, 'admin_login.html')


def mfa_verify_view(request):
    user_id = request.session.get('pre_mfa_user_id')
    mfa_code = request.session.get('mfa_code')
    
    if not user_id or not mfa_code:
        return redirect('login_view')
        
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        code_entered = request.POST.get('code')
        if code_entered == mfa_code:
            # Clear pre-mfa variables
            del request.session['pre_mfa_user_id']
            del request.session['mfa_code']
            auth_login(request, user)
            messages.success(request, f"Welcome back, operator {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "MFA Verification failed. Decryption key mismatch.")
            
    return render(request, 'mfa.html', {'mfa_code': mfa_code, 'username': user.username})

def logout_view(request):
    auth_logout(request)
    messages.success(request, "Session terminated. Safe travels in the net.")
    return redirect('home')

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    can_access = False
    if request.user.is_authenticated and order.user == request.user:
        can_access = True
    elif str(order_id) in [str(oid) for oid in request.session.get('my_orders', [])]:
        can_access = True
    elif request.user.is_staff:
        can_access = True
        
    if not can_access:
        messages.error(request, "Access unauthorized to this data node.")
        return redirect('home')
        
    return render(request, 'order_detail.html', {'order': order})

def invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    can_access = False
    if request.user.is_authenticated and order.user == request.user:
        can_access = True
    elif str(order_id) in [str(oid) for oid in request.session.get('my_orders', [])]:
        can_access = True
    elif request.user.is_staff:
        can_access = True
        
    if not can_access:
        messages.error(request, "Access unauthorized to this data node.")
        return redirect('home')
        
    return render(request, 'invoice.html', {'order': order})

@login_required
def create_ticket(request):
    if request.method == 'POST':
        ticket_type = request.POST.get('ticket_type', 'Support')
        order_id = request.POST.get('order_id')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=int(order_id), user=request.user)
            except (Order.DoesNotExist, ValueError):
                pass
                
        if subject and message:
            SupportTicket.objects.create(
                user=request.user,
                order=order,
                ticket_type=ticket_type,
                subject=subject,
                message=message
            )
            messages.success(request, "Ticket submitted. Our NetRunners are analyzing it.")
        else:
            messages.error(request, "Subject and message content are required.")
            
    return redirect('dashboard')

@login_required
def feedback_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not subject or not message:
            messages.error(request, "Please provide both subject and feedback message.")
            return render(request, 'feedback.html')

        SupportTicket.objects.create(
            user=request.user,
            ticket_type='Feedback',
            subject=subject,
            message=message
        )
        messages.success(request, "Thank you for your feedback. We appreciate your input.")
        return redirect('dashboard')

    return render(request, 'feedback.html')

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    return render(request, 'ticket_detail.html', {'ticket': ticket})

@staff_member_required
def staff_dashboard(request):
    products = Product.objects.all().order_by('stock')
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter/Search orders
    query = request.GET.get('q', '')
    if query:
        orders = orders.filter(
            models.Q(id__icontains=query) |
            models.Q(full_name__icontains=query) |
            models.Q(email__icontains=query)
        )
        
    low_stock_products = Product.objects.filter(stock__lt=10)
    out_of_stock_products = Product.objects.filter(stock=0)
    
    return render(request, 'admin_dashboard.html', {
        'products': products,
        'orders': orders,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'query': query
    })

@require_POST
@staff_member_required
def adjust_price_ajax(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        new_price = Decimal(str(data.get('price')))
        
        product = Product.objects.get(id=product_id)
        product.price = new_price
        product.save()
        return JsonResponse({'status': 'success', 'price': str(product.price)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@staff_member_required
def update_order_status_ajax(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
        return JsonResponse({'status': 'success', 'status_label': order.status})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Admin Profile & User Management Views
@staff_member_required
def admin_profile(request):
    """Display admin profile with statistics."""
    admin_user = request.user
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(models.Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lt=10).count()
    
    try:
        admin_profile = admin_user.profile
    except UserProfile.DoesNotExist:
        admin_profile = UserProfile.objects.create(user=admin_user)
    
    context = {
        'admin_user': admin_user,
        'admin_profile': admin_profile,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'admin_profile.html', context)


@staff_member_required
def manage_users(request):
    """List all users with management options."""
    search_query = request.GET.get('q', '')
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'manage_users.html', context)


@staff_member_required
def user_detail(request, user_id):
    """View user details and orders."""
    user = get_object_or_404(User, id=user_id)
    user_orders = Order.objects.filter(user=user).order_by('-created_at')
    user_tickets = SupportTicket.objects.filter(user=user).order_by('-created_at')
    
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'user_orders': user_orders,
        'user_tickets': user_tickets,
    }
    return render(request, 'user_detail.html', context)


@staff_member_required
def user_edit(request, user_id):
    """Edit user details."""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()
        
        # Update user profile
        try:
            user_profile = user.profile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)
        
        user_profile.phone = request.POST.get('phone', '')
        user_profile.shipping_address = request.POST.get('shipping_address', '')
        user_profile.save()
        
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect('user_detail', user_id=user.id)
    
    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    context = {
        'user': user,
        'user_profile': user_profile,
    }
    return render(request, 'user_edit.html', context)


@staff_member_required
def user_create(request):
    """Create a new user."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required.")
            return render(request, 'user_create.html')
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'user_create.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return render(request, 'user_create.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' already exists.")
            return render(request, 'user_create.html')

        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        messages.success(request, f"User '{username}' created successfully.")
        return redirect('manage_users')
    
    return render(request, 'user_create.html')


@staff_member_required
def user_delete(request, user_id):
    """Delete a user."""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deletion of superuser
    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser account.")
        return redirect('manage_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully.")
        return redirect('manage_users')
    
    context = {'user': user}
    return render(request, 'user_confirm_delete.html', context)
