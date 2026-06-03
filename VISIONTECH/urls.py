from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.catalog, name='catalog'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('builder/', views.pc_builder, name='pc_builder'),
    
    # Cart routes
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/add-custom-rig/', views.cart_add_custom_rig, name='cart_add_custom_rig'),
    path('checkout/', views.checkout, name='checkout'),
    
    # User Profile & Auth routes
    path('register/', views.register_view, name='register_view'),
    path('login/', views.login_view, name='login_view'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('login/mfa/', views.mfa_verify_view, name='mfa_verify_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('brands/', views.brand_list, name='brand_list'),
    
    # Order tracking & invoice routes
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/invoice/', views.invoice_view, name='invoice_view'),
    
    # Tech Support & RMA routes
    path('support/ticket/create/', views.create_ticket, name='create_ticket'),
    path('support/ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # Admin / Staff Dashboard routes
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/adjust-price/', views.adjust_price_ajax, name='adjust_price_ajax'),
    path('staff/update-status/', views.update_order_status_ajax, name='update_order_status_ajax'),
    # Admin Profile & User Management routes
    path('admin/profile/', views.admin_profile, name='admin_profile'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('admin/users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    # Custom admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/brands/add/', views.brand_create, name='brand_create'),
    path('admin-panel/brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('admin-panel/brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    path('admin-panel/products/add/', views.product_create, name='product_create'),
]
