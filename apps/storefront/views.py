from django.shortcuts import render,get_object_or_404
from apps.catalog.models import Product,Category
from apps.orders.models import Order
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Avg, Count
from apps.reviews.models import Review
def home(request):
 products=Product.objects.filter(active=True).prefetch_related('variants','images').select_related('category').order_by('-created_at')[:12]
 return render(request,'store/home.html',{'products':products,'categories':Category.objects.all()[:12]})
def listing(request):
 products=Product.objects.filter(active=True).prefetch_related('variants','images')
 q=request.GET.get('q','').strip()
 if q:products=products.filter(name__icontains=q)
 category=request.GET.get('category')
 if category:products=products.filter(category__slug=category)
 sort=request.GET.get('sort','newest')
 if sort in ('price_asc','price_desc'):
  products=products.annotate(min_price=Min('variants__price')).order_by('min_price' if sort=='price_asc' else '-min_price','id')
 elif sort=='name':products=products.order_by('name','id')
 else:sort='newest';products=products.order_by('-created_at')
 return render(request,'store/list.html',{'products':products[:60],'categories':Category.objects.all(),'query':q,'selected_category':category,'sort':sort})
def detail(request,slug):
 product=get_object_or_404(Product.objects.prefetch_related('variants','images'),slug=slug,active=True)
 reviews=Review.objects.filter(product=product,approved=True).select_related('user').order_by('-created_at')
 summary=reviews.aggregate(avg=Avg('rating'),count=Count('id'))
 return render(request,'store/detail.html',{'product':product,'reviews':reviews[:30],'review_summary':summary})
def cart(request):return render(request,'store/cart.html')
def checkout(request):return render(request,'store/checkout.html')
def orders(request):return render(request,'store/orders.html')
def order_confirmation(request,order_id):return render(request,'store/order_confirmation.html',{'order_id':order_id})
def dashboard(request):return render(request,'store/dashboard.html')

def login_page(request): return render(request,'store/login.html')
def register_page(request): return render(request,'store/register.html')

def seller_dashboard(request): return render(request,'store/seller.html')
def seller_orders_page(request): return render(request,'store/seller_orders.html')
