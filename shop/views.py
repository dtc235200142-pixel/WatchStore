from django.shortcuts import render
from .models import Product, Category, Brand
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm
)
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Order, OrderDetail
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    keyword = request.GET.get('q', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')

    if keyword:
        products = products.filter(
            name__icontains=keyword
        )

    if category.isdigit():
        products = products.filter(
            category_id=category
        )

    if brand.isdigit():
        products = products.filter(
            brand_id=brand
        )

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'keyword': keyword,
        'selected_category': category,
        'selected_brand': brand,
    }

    return render(request, 'home.html', context)
    # Đăng ký tài khoản
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request, 'Đăng ký thành công!'
            )
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form': form
    })


# Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(
            request, data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form
    })


# Đăng xuất
@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')

# Thêm sản phẩm vào giỏ hàng
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product, id=product_id
    )

    cart = request.session.get('cart', {})
    key = str(product_id)

    quantity = cart.get(key, 0) + 1

    if quantity <= product.stock:
        cart[key] = quantity

        request.session['cart'] = cart

        messages.success(
            request, 'Đã thêm vào giỏ hàng!'
        )
    else:
        messages.error(
            request, 'Sản phẩm không đủ tồn kho!'
        )

    return redirect('cart')


# Hiển thị giỏ hàng
def cart_view(request):
    cart = request.session.get('cart', {})

    items = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.objects.filter(
            id=product_id
        ).first()

        if product:
            subtotal = product.price * quantity

            total += subtotal

            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
    })


# Xóa sản phẩm khỏi giỏ hàng
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    key = str(product_id)

    if key in cart:
        del cart[key]

    request.session['cart'] = cart

    return redirect('cart')


# Cập nhật số lượng sản phẩm
@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(
        Product, id=product_id
    )

    cart = request.session.get('cart', {})
    key = str(product_id)

    if key not in cart:
        return redirect('cart')

    try:
        quantity = int(
            request.POST.get('quantity', 1)
        )
    except (ValueError, TypeError):
        messages.error(
            request, 'Số lượng không hợp lệ!'
        )
        return redirect('cart')

    if 1 <= quantity <= product.stock:
        cart[key] = quantity

        request.session['cart'] = cart
    else:
        messages.error(
            request, 'Số lượng không hợp lệ!'
        )

    return redirect('cart')

@login_required(login_url='login')
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, 'Giỏ hàng đang trống!')
        return redirect('cart')

    items = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.objects.filter(
            id=product_id
        ).first()

        if not product:
            messages.error(request, 'Sản phẩm không còn tồn tại!')
            return redirect('cart')

        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not full_name or not phone or not address:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin!')
            return redirect('checkout')

        try:
            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    total_amount=0
                )

                total = 0

                for product_id, quantity in sorted(cart.items()):

                    product = Product.objects.select_for_update().get(
                        id=product_id
                    )

                    if quantity < 1 or quantity > product.stock:
                        raise ValueError(
                            f'{product.name} không đủ tồn kho!'
                        )

                    OrderDetail.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

                    total += product.price * quantity

                    product.stock -= quantity
                    product.save(update_fields=['stock'])

                order.total_amount = total
                order.save(update_fields=['total_amount'])

        except (ValueError, Product.DoesNotExist):
            messages.error(
                request,
                'Sản phẩm không còn hoặc không đủ tồn kho!'
            )
            return redirect('cart')

        request.session['cart'] = {}

        messages.success(request, 'Đặt hàng thành công!')

        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })


@login_required(login_url='login')
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order
    })


@login_required(login_url='login')
def order_history(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'orders.html', {
        'orders': orders
    })

# ======================================
# DASHBOARD THỐNG KÊ ADMIN
# ======================================

@staff_member_required
def dashboard(request):

    # 1. Thống kê tổng số sản phẩm
    total_products = Product.objects.count()

    # 2. Thống kê tổng số đơn hàng
    total_orders = Order.objects.count()

    # 3. Tổng giá trị tất cả đơn hàng
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # 4. Doanh số đơn hàng đã hoàn thành
    completed_revenue = Order.objects.filter(
        status='completed'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # 5. Tổng số sản phẩm đã đặt
    total_sold = OrderDetail.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # 6. Tổng số lượng tồn kho
    total_stock = Product.objects.aggregate(
        total=Sum('stock')
    )['total'] or 0

    # 7. Thống kê trạng thái đơn hàng
    pending_orders = Order.objects.filter(
        status='pending'
    ).count()

    confirmed_orders = Order.objects.filter(
        status='confirmed'
    ).count()

    shipping_orders = Order.objects.filter(
        status='shipping'
    ).count()

    completed_orders = Order.objects.filter(
        status='completed'
    ).count()

    # 8. Thống kê tồn kho từng sản phẩm
    products = Product.objects.all()

    inventory = []

    for product in products:

        sold = OrderDetail.objects.filter(
            product=product
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        stock = product.stock

        initial_stock = stock + sold

        if initial_stock > 0:

            stock_percent = round(
                stock / initial_stock * 100, 1
            )

            sold_percent = round(
                sold / initial_stock * 100, 1
            )

        else:

            stock_percent = 0
            sold_percent = 0

        inventory.append({
            'name': product.name,
            'initial_stock': initial_stock,
            'sold': sold,
            'stock': stock,
            'stock_percent': stock_percent,
            'sold_percent': sold_percent,
        })

    # 9. Lấy 5 đơn hàng gần nhất
    recent_orders = Order.objects.order_by(
        '-created_at'
    )[:5]

    # 10. Dữ liệu biểu đồ
    chart_labels = [
        item['name'] for item in inventory
    ]

    chart_stock = [
        item['stock'] for item in inventory
    ]

    chart_sold = [
        item['sold'] for item in inventory
    ]

    status_data = [
        pending_orders,
        confirmed_orders,
        shipping_orders,
        completed_orders
    ]

    # 11. Truyền dữ liệu sang HTML
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'completed_revenue': completed_revenue,
        'total_sold': total_sold,
        'total_stock': total_stock,

        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'shipping_orders': shipping_orders,
        'completed_orders': completed_orders,

        'inventory': inventory,
        'recent_orders': recent_orders,

        'chart_labels': chart_labels,
        'chart_stock': chart_stock,
        'chart_sold': chart_sold,
        'status_data': status_data,
    }

    return render(
        request,
        'dashboard.html',
        context
    )