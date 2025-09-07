from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Product, Category, CartItem
from django.db import transaction
from .models import Order, OrderItem
from django.db.models import Sum

def home(request):
    return render(request, 'shop/home.html')

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < quantity:
        messages.error(request, 'אין מספיק מלאי')
        return redirect('shop:product_detail', id=product.id, slug=product.slug)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, 'אין מספיק מלאי')
            return redirect('shop:cart_detail')
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} נוסף לעגלה')
    return redirect('shop:cart_detail')

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.quantity * item.product.price for item in cart_items)
    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} הוסר מהעגלה')
    return redirect('shop:cart_detail')

@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > cart_item.product.stock:
            messages.error(request, 'אין מספיק מלאי')
        elif quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'העגלה עודכנה')
        else:
            cart_item.delete()
            messages.success(request, 'המוצר הוסר מהעגלה')
    
    return redirect('shop:cart_detail')

@login_required
def checkout(request):
    """Display checkout form"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'העגלה שלך ריקה')
        return redirect('shop:cart')
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
@login_required
def process_order(request):
    """Process the checkout form and create order"""
    if request.method != 'POST':
        return redirect('shop:checkout')
    
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'העגלה שלך ריקה')
        return redirect('shop:cart_detail')  # Fixed: was 'shop:cart'
    
    # Get form data
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    postal_code = request.POST.get('postal_code', '').strip()
    
    # Basic validation
    required_fields = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    
    if missing_fields:
        messages.error(request, 'אנא מלא את כל השדות הנדרשים')
        return redirect('shop:checkout')
    
    try:
        with transaction.atomic():
            # Calculate total
            total = sum(item.product.price * item.quantity for item in cart_items)
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postal_code=postal_code,
                total_amount=total
            )
            
            # Create order items and update stock
            for cart_item in cart_items:
                if cart_item.product.stock < cart_item.quantity:
                    raise ValueError(f'מוצר {cart_item.product.name} אינו זמין במלאי מספיק')
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'ההזמנה נוצרה בהצלחה! מספר הזמנה: {order.order_number}')
            return redirect('shop:order_confirmation', order_number=order.order_number)
            
    except ValueError as e:
        messages.error(request, str(e))
        print(e)
        return redirect('shop:checkout')
    except Exception as e:
        print(e)
        messages.error(request, 'אירעה שגיאה בעיבוד ההזמנה. אנא נסה שוב.')
        return redirect('shop:checkout')

@login_required
def order_confirmation(request, order_number):
    """Display order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_confirmation.html', context)


@login_required
def user_profile(request):
    """Display user profile with order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created')
    
    # Calculate total donations for stats
    total_amount = orders.aggregate(total_amount__sum=Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'orders': orders,
        'total_donations': total_amount,
    }
    return render(request, 'shop/user_profile.html', context)

@login_required
def order_detail(request, order_number):
    """Display detailed view of a specific order"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'shop/order_detail.html', {
        'order': order
    })