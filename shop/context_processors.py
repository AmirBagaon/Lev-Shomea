def cart_context(request):
    """Simple context processor for cart count"""
    cart_count = 0
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            from .models import CartItem
            cart_count = CartItem.objects.filter(user=request.user).count()
        except:
            cart_count = 0
    return {'cart_count': cart_count}