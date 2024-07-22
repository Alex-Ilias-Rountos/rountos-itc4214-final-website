from django.urls import path
from .views import product_list
from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
    path('profile/', views.get_user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('products/', views.product_list, name='product_list'),
	path('toggle_bookmark/<int:product_id>/', views.toggle_bookmark, name='toggle_bookmark'),

]