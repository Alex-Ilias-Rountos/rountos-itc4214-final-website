from django.shortcuts import render
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from .models import * 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from . utils import cookieCart
from django.shortcuts import render, redirect
from .forms import UpdateUserForm
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Bookmark
from django.shortcuts import get_object_or_404


# Create your views here.


@login_required
def toggle_bookmark(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = Product.objects.get(id=product_id)
        bookmark, created = Bookmark.objects.get_or_create(user=user, product=product)

        if not created:
            bookmark.delete()
            return JsonResponse({'bookmarked': False})
        else:
            return JsonResponse({'bookmarked': True})

@login_required
def product_list(request):
    query = request.GET.get('q')
    filter_category = request.GET.get('filter_category')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if filter_category:
        if filter_category == 'True':
            products = products.filter(digital=True)
        elif filter_category == 'False':
            products = products.filter(digital=False)

    user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'store/store.html', {'products': products, 'bookmarked_products': user_bookmarks})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()

            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)

    return render(request, 'users/profile.html', {'user_form': user_form})




def user_logout(request):
    logout(request)
    return redirect('login')


def get_user_profile(response):
    return render(response, 'store/profile.html')

def store(request):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

            # Get bookmarked products for the logged-in user
            bookmarked_products = Bookmark.objects.filter(user=request.user).values_list('product_id', flat=True)

        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
            bookmarked_products = []

        products = Product.objects.all()
        context = {
            'products': products,
            'cartItems': cartItems,
            'bookmarked_products': bookmarked_products,
        }
        return render(request, 'store/store.html', context)
    except ObjectDoesNotExist:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        bookmarked_products = []

        products = Product.objects.all()
        context = {
            'products': products,
            'cartItems': cartItems,
            'bookmarked_products': bookmarked_products,
        }
        return render(request, 'store/store.html', context)

def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']				

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

    

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']	

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)	#if it exists, update the items

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


