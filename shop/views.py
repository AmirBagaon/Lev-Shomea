from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Product, Category, CartItem

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