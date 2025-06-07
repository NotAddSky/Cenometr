from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'complaints', ComplaintViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('complaints/submit/', views.submit_complaint, name='submit_complaint'),
    path('complaints/ajax/', views.submit_complaint_ajax,
         name='submit_complaint_ajax'),
    path('owner/complaint/<int:complaint_id>/resolve/',
         views.resolve_complaint, name='resolve_complaint'),
    path('complaint/<int:complaint_id>/update/',
         views.update_complaint, name='update_complaint'),
    path('store-autocomplete/', AvailableStoreAutocomplete.as_view(),
         name='store-autocomplete'),
    path('product-autocomplete/', ProductAutocomplete.as_view(),
         name='product-autocomplete'),
    path('owner/', owner_dashboard, name='owner_dashboard'),
    path('owner/price/<int:pk>/edit/', edit_price, name='edit_price'),
    path('owner/price/add/', add_price, name='add_price'),
    path('accounts/register/', register, name='register'),
    path('owner/price/<int:pk>/update/', update_price, name='update_price'),
    path('owner/price/<int:pk>/delete/', delete_price, name='delete_price'),
    path('owner/modal/store-select/', views.store_modal, name='store_modal'),
    path('product/<int:pk>/detail/', views.product_detail_ajax,
         name='product_detail_ajax'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/add/<int:product_id>/',
         views.add_favorite, name='add_favorite'),
    path('favorites/remove/<int:product_id>/',
         views.remove_favorite, name='remove_favorite'),
    path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('accounts/', include('allauth.urls')),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('api/todo/', views.todo_list_api, name='todo_list_api'),
    path('api/todo/create/', views.todo_create_api, name='todo_create_api'),
    path('api/todo/<int:task_id>/update/',
         views.todo_update_api, name='todo_update_api'),
    path('api/todo/<int:task_id>/delete/',
         views.todo_delete_api, name='todo_delete_api'),
]
