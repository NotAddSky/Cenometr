from django.urls import path
from admin_panel import views
from .views import *

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('stores/', views.store_list, name='admin_store_list'),
    path('products/', views.product_list, name='admin_product_list'),
    path('categories/', views.category_list, name='admin_category_list'),
    path('manufacturers/', views.manufacturer_list,
         name='admin_manufacturer_list'),
    path('suggestions/', suggestion_list, name='admin_suggestion_list'),
    path('suggestions/pending/', views.moderate_suggestions,
         name='admin_moderate_suggestions'),
    path('suggestions/<int:pk>/', suggestion_detail,
         name='admin_suggestion_detail'),
    path('suggestions/<int:suggestion_id>/approve/',
         approve_suggestion, name='approve_suggestion'),
    path('suggestions/<int:suggestion_id>/reject/',
         reject_suggestion, name='reject_suggestion'),
    path('suggest-product/', suggest_product_api,
         name='suggest_product_api'),
    path('moderate-suggestions/', moderate_suggestions,
         name='moderate_suggestions'),
    path('suggestions/<int:suggestion_id>/approve/',
         approve_suggestion, name='approve_suggestion'),
    path('suggestions/<int:suggestion_id>/reject/',
         reject_suggestion, name='reject_suggestion'),
    path('manufacturers/', views.manufacturer_list,
         name='admin_manufacturer_list'),
    path('manufacturers/add/', views.add_manufacturer, name='add_manufacturer'),
    path('manufacturers/<int:manufacturer_id>/edit/',
         views.edit_manufacturer, name='edit_manufacturer'),
    path('manufacturers/<int:manufacturer_id>/delete/',
         views.delete_manufacturer, name='delete_manufacturer'),

    path('products/', views.product_management, name='admin_product_list'),

]
