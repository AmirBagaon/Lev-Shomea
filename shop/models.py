# shop/models.py - Updated version with all required fields
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Marketer(models.Model):
    """משווק - מופיע בהזמנות ובמשתמשים"""
    first_name = models.CharField(max_length=50, verbose_name='שם פרטי')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='שם משפחה')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='משתמש במערכת')
    phone = models.CharField(max_length=20, blank=True, verbose_name='טלפון')
    email = models.EmailField(blank=True, verbose_name='אימייל')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הוספה')
    
    class Meta:
        verbose_name = 'משווק'
        verbose_name_plural = 'משווקים'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Event(models.Model):
    """אירוע - מופיע בהזמנות"""
    name = models.CharField(max_length=100, verbose_name='שם האירוע')
    description = models.TextField(blank=True, verbose_name='תיאור')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הוספה')
    
    class Meta:
        verbose_name = 'אירוע'
        verbose_name_plural = 'אירועים'
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """קטגוריית מוצר"""
    name = models.CharField(max_length=100, verbose_name='שם הקטגוריה')
    slug = models.SlugField(unique=True, verbose_name='כתובת URL')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הוספה')
    
    class Meta:
        verbose_name = 'קטגוריה'
        verbose_name_plural = 'קטגוריות'
    
    def __str__(self):
        return self.name

class Kashrut(models.Model):
    """כשרות - לכל מוצר"""
    name = models.CharField(max_length=100, verbose_name='רמת כשרות')
    description = models.TextField(blank=True, verbose_name='תיאור')
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הוספה')
    
    class Meta:
        verbose_name = 'כשרות'
        verbose_name_plural = 'כשרויות'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """מוצר"""
    name = models.CharField(max_length=200, verbose_name='שם המוצר')
    slug = models.SlugField(unique=True, verbose_name='כתובת URL')
    description = models.TextField(verbose_name='תיאור')
    
    # קטגוריה וכשרות
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='קטגוריה')
    kashrut = models.ForeignKey(Kashrut, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='כשרות')
    
    # ספק
    supplier = models.CharField(max_length=200, verbose_name='ספק')
    
    # מחיר ומלאי
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='מחיר')
    stock = models.PositiveIntegerField(default=999999, verbose_name='מלאי', help_text='ברירת מחדל: אינסופי')
    unlimited_stock = models.BooleanField(default=True, verbose_name='מלאי אינסופי')
    
    # כמות הזמנות
    total_orders = models.PositiveIntegerField(default=0, verbose_name='כמות הזמנות')
    
    # תמונה
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='תמונה')
    
    # סטטוס
    is_active = models.BooleanField(default=True, verbose_name='פעיל')
    
    # תאריכים
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך יצירה')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='תאריך עדכון')
    
    class Meta:
        verbose_name = 'מוצר'
        verbose_name_plural = 'מוצרים'
    
    def __str__(self):
        return self.name
    
    @property
    def available(self):
        """בדיקה אם המוצר זמין"""
        if not self.is_active:
            return False
        if self.unlimited_stock:
            return True
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """הפחתת מלאי"""
        if not self.unlimited_stock and self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        elif self.unlimited_stock:
            return True
        return False

class CartItem(models.Model):
    """פריט בעגלת קניות"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='משתמש')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='מוצר')
    quantity = models.PositiveIntegerField(default=1, verbose_name='כמות')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הוספה')
    
    class Meta:
        unique_together = ['user', 'product']
        verbose_name = 'פריט בעגלה'
        verbose_name_plural = 'פריטים בעגלה'
    
    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
    
    def get_total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    """הזמנה"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'ממתין'),
        ('processing', 'בטיפול'),
        ('shipped', 'נשלח'),
        ('delivered', 'הגיע'),
        ('cancelled', 'בוטל'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'ממתין לתשלום'),
        ('paid', 'שולם'),
        ('failed', 'נכשל'),
        ('refunded', 'הוחזר'),
    ]
    
    # מזהה הזמנה
    order_number = models.CharField(max_length=20, unique=True, verbose_name='מספר הזמנה')
    
    # קישור למשתמש
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='משתמש')
    
    # פרטי לקוח (נשמרים בהזמנה)
    first_name = models.CharField(max_length=50, verbose_name='שם פרטי')
    last_name = models.CharField(max_length=50, verbose_name='שם משפחה')
    email = models.EmailField(verbose_name='אימייל')
    phone = models.CharField(max_length=20, verbose_name='טלפון')
    
    # כתובת משלוח (אופציונלי)
    address = models.CharField(max_length=200, blank=True, verbose_name='כתובת')
    city = models.CharField(max_length=50, blank=True, verbose_name='עיר')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='מיקוד')
    
    # פרטי הזמנה
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='סכום כולל')
    total_items = models.PositiveIntegerField(default=0, verbose_name='כמות פריטים')
    
    # סטטוס
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name='סטטוס הזמנה')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='מצב תשלום')
    
    # משווק ואירוע
    marketer = models.ForeignKey(Marketer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='משווק')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='אירוע')
    
    # תאריכים
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך הזמנה')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='תאריך עדכון')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'הזמנה'
        verbose_name_plural = 'הזמנות'
    
    def __str__(self):
        return f'הזמנה {self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # יצירת מספר הזמנה יניק
            self.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """פריט בהזמנה"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='הזמנה')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='מוצר')
    quantity = models.PositiveIntegerField(verbose_name='כמות')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='מחיר ברגע ההזמנה')
    
    class Meta:
        verbose_name = 'פריט בהזמנה'
        verbose_name_plural = 'פריטים בהזמנה'
    
    def __str__(self):
        return f'{self.order.order_number} - {self.product.name}'
    
    def get_total_price(self):
        return self.quantity * self.price