from datetime import timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.db.models import OuterRef, Subquery
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.urls import reverse
from rest_framework import viewsets
from .models import *
from .serializers import *
from dal import autocomplete
from PIL import Image
from .forms import *
from .decorators import role_required
import json
import io
import hashlib
import hmac


@role_required('user')
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    complaints = Complaint.objects.filter(user=user).select_related(
        'product', 'store').order_by('-created_at')

    return render(request, 'catalog/profile.html', {
        'form': form,
        'user': user,
        'complaints': complaints,
    })


@role_required('user')
def upload_avatar(request):
    image_file = request.FILES.get('avatar')
    if not image_file:
        return JsonResponse({'success': False, 'error': 'Файл не передан'}, status=400)

    try:
        image = Image.open(image_file).convert('RGB')
        buffer = io.BytesIO()
        image.save(buffer, format='WEBP', quality=95)
        buffer.seek(0)

        filename = 'avatar.webp'
        upload_path = user_avatar_path(request.user, filename)

        if request.user.avatar and request.user.avatar.name != upload_path:
            request.user.avatar.delete(save=False)

        request.user.avatar.save(
            upload_path, ContentFile(buffer.getvalue()), save=True)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@role_required('owner')
def owner_dashboard(request):
    user = request.user

    if user.role == 'admin':
        store_ids = Store.objects.values_list('id', flat=True)
    else:
        store_ids = user.stores.values_list('id', flat=True)

    selected_store_id = request.GET.get('store')
    selected_store = None
    products = []
    search = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')

    order = request.GET.get('order', 'name')

    if not selected_store_id:
        stores = Store.objects.filter(id__in=store_ids)

        if stores.count() == 1:
            return redirect(f"{request.path}?store={stores.first().id}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(
                'catalog/includes/store_modal.html', {'stores': stores})
            return JsonResponse({'html': html})

        return render(request, 'catalog/owner_dashboard.html', {
            'stores': stores,
            'store_modal_needed': True
        })

    selected_store = Store.objects.filter(
        id=selected_store_id, id__in=store_ids).first()

    if selected_store:
        prices = Price.objects.filter(store=selected_store).select_related(
            'product__category', 'product__manufacturer')

        if search:
            prices = prices.filter(product__name__icontains=search)
        if category_id:
            prices = prices.filter(product__category_id=category_id)
        if manufacturer_id:
            prices = prices.filter(product__manufacturer_id=manufacturer_id)

        if order == 'created':
            prices = prices.order_by('-id')
        else:
            prices = prices.order_by('product__name')

        products = prices

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table_html = render_to_string('catalog/includes/price_table_body.html', {
                'products': products
            }, request=request)
            return JsonResponse({'html': table_html})

    complaints = []
    if selected_store:
        complaints = Complaint.objects.filter(store=selected_store).select_related(
            'product', 'store').order_by('-created_at')

    context = {
        'stores': Store.objects.filter(id__in=store_ids),
        'selected_store': selected_store,
        'products': products,
        'categories': ProductCategory.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'selected_category': category_id,
        'selected_manufacturer': manufacturer_id,
        'search_query': search,
        'order': order,
        'complaints': complaints
    }

    return render(request, 'catalog/owner_dashboard.html', context)


@role_required('user')
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'product__category', 'product__manufacturer')

    for fav in favorites:
        price = Price.objects.filter(product=fav.product).order_by(
            'price').select_related('store').first()
        if price:
            fav.min_price = price.price
            fav.store_name = price.store.name
            fav.store_address = price.store.full_address
        else:
            fav.min_price = None
            fav.store_name = None
            fav.store_address = None

    return render(request, 'catalog/favorites.html', {
        'favorites': favorites
    })


@require_POST
@role_required('user')
def add_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect(request.META.get('HTTP_REFERER', 'favorites'))


@require_POST
@role_required('user')
def remove_favorite(request, product_id):
    favorite = Favorite.objects.filter(
        user=request.user, product_id=product_id).first()
    if favorite:
        favorite.delete()
    return redirect('favorites')


@require_POST
def toggle_favorite(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        from django.shortcuts import redirect
        return redirect('login')

    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'No product ID'}, status=400)

    product = get_object_or_404(Product, pk=product_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, product=product)

    if not created:
        favorite.delete()
        return JsonResponse({'success': True, 'is_favorite': False})
    else:
        return JsonResponse({'success': True, 'is_favorite': True})


@role_required('owner')
def store_modal(request):
    user = request.user
    if user.role == 'admin':
        stores = Store.objects.all()
    else:
        stores = user.stores.all()

    if stores.count() <= 1:
        return JsonResponse({'html': ''})

    html = render_to_string(
        'catalog/includes/store_modal.html', {'stores': stores})
    return JsonResponse({'html': html})


def product_detail_ajax(request, pk):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Invalid request")

    product = get_object_or_404(Product, pk=pk)
    prices_qs = Price.objects.filter(
        product=product).select_related('store__address_base')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(prices_qs, 5)
    page_obj = paginator.get_page(page_number)

    html = render_to_string('catalog/includes/product_detail_modal.html', {
        'product': product,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
    }, request=request)

    return JsonResponse({'html': html})


@role_required('owner')
def add_price(request):
    store_id = request.GET.get('store')
    if not store_id:
        return HttpResponseBadRequest("Не выбран магазин.")

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return HttpResponseBadRequest("Магазин не найден.")

    if request.user.role != 'admin' and request.user not in store.owners.all():
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = PriceAdminForm(
            request.POST, current_user=request.user, current_store=store)
        if form.is_valid():
            price = form.save(commit=False)
            price.store = store
            price.save()
            return HttpResponse(status=204)
    else:
        form = PriceAdminForm(current_user=request.user, current_store=store)

    return render(request, 'catalog/includes/add_price_form.html', {
        'form': form,
        'store': store
    })


@role_required('owner')
def update_price(request, pk):
    if request.method == 'POST':
        try:
            price = Price.objects.get(pk=pk)
        except Price.DoesNotExist:
            return JsonResponse({'error': 'Price not found'}, status=404)

        if request.user.role != 'admin' and request.user not in price.store.owners.all():
            return JsonResponse({'error': 'Access denied'}, status=403)

        new_price = request.POST.get('price')

        try:
            price_value = float(new_price)
            if price_value < 0 or price_value > 9999999:
                return JsonResponse({'error': 'Цена должна быть от 0 до 9 999 999'}, status=400)

            price.price = price_value
            price.save()
            return JsonResponse({'status': 'success'})

        except ValueError:
            return JsonResponse({'error': 'Некорректная цена'}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)


@role_required('owner')
def delete_price(request, pk):
    if request.method == 'POST':
        try:
            price = Price.objects.get(pk=pk)
        except Price.DoesNotExist:
            return JsonResponse({'error': 'Price not found'}, status=404)

        if request.user.role != 'admin' and request.user not in price.store.owners.all():
            return JsonResponse({'error': 'Access denied'}, status=403)

        price.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@role_required('owner')
def edit_price(request, pk):
    price = get_object_or_404(Price, pk=pk)

    if request.user.role != 'admin' and request.user not in price.store.owners.all():
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = PriceAdminForm(request.POST, instance=price)
        form.current_user = request.user
        if form.is_valid():
            form.save()
            return HttpResponse(status=204)
        else:
            html = render_to_string(
                'catalog/includes/edit_price_form.html', {'form': form, 'price': price}, request=request)
            return HttpResponseBadRequest(html)
    else:
        form = PriceAdminForm(instance=price)
        form.current_user = request.user

    return render(request, 'catalog/includes/edit_price_form.html', {
        'form': form,
        'price': price
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.role = 'user'
            user.save()
            login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def verify_telegram_auth(data):
    token = settings.TELEGRAM_BOT_TOKEN
    secret_key = hashlib.sha256(token.encode()).digest()

    auth_data = {k: v for k, v in data.items() if k != 'hash'}
    sorted_data = sorted(f"{k}={v}" for k, v in auth_data.items())
    data_check_string = '\n'.join(sorted_data)
    h = hmac.new(secret_key, data_check_string.encode(),
                 hashlib.sha256).hexdigest()

    return h == data.get('hash')


@csrf_exempt
def telegram_auth(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if not verify_telegram_auth(data):
                return JsonResponse({'success': False, 'error': 'Недостоверная подпись Telegram'})

            telegram_id = data.get('id')
            username = data.get('username', f'tg_user_{telegram_id}')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')

            if not telegram_id:
                return JsonResponse({'success': False, 'error': 'Нет Telegram ID'})

            user, _ = User.objects.get_or_create(
                username=f'tg_{telegram_id}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{telegram_id}@telegram.local'
                }
            )

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})


class AvailableStoreAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        queryset = Store.objects.none()
        product_id = self.forwarded.get('product')

        if product_id:
            used = Price.objects.filter(
                product_id=product_id).values_list('store_id', flat=True)
            queryset = Store.objects.exclude(id__in=used)

        return queryset


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()
        store_id = self.forwarded.get('store')

        if store_id:
            used_products = Price.objects.filter(
                store_id=store_id).values_list('product_id', flat=True)
            qs = qs.exclude(id__in=used_products)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


@role_required('user')
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('home')
    else:
        form = ComplaintForm()

    return render(request, 'catalog/complaint_form.html', {'form': form})


@role_required('user')
def submit_complaint_ajax(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        store_id = request.POST.get('store_id')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not (product_id and store_id and description):
            return JsonResponse({'success': False, 'error': 'Заполните все поля'})

        try:
            complaint = Complaint.objects.create(
                user=request.user,
                product_id=product_id,
                store_id=store_id,
                description=description,
                image=image,
                status='new'
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Недопустимый метод'})


@role_required('owner')
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.user.role == 'admin' or complaint.store in request.user.stores.all():
        complaint.status = 'resolved'
        complaint.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('owner_dashboard')))


@role_required('owner')
def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.user.role not in ['admin', 'owner'] or complaint.store not in request.user.stores.all():
        return render(request, '403.html', status=403)

    complaint.status = request.POST.get('status', complaint.status)
    complaint.response = request.POST.get('response', complaint.response)
    complaint.save()

    return HttpResponseRedirect(reverse('owner_dashboard') + f'?store={complaint.store.id}')


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class AvailableStoreAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        queryset = Store.objects.all()
        product_id = self.forwarded.get('product')

        if product_id:
            used = Price.objects.filter(
                product_id=product_id).values_list('store_id', flat=True)
            queryset = queryset.exclude(id__in=used)

        return queryset


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)


@admin_required
@require_http_methods(["GET"])
def todo_list_api(request):
    tasks = list(TodoTask.objects.order_by(
        '-created_at').values('id', 'title', 'status'))
    return JsonResponse({'tasks': tasks})


@admin_required
@require_http_methods(["POST"])
def todo_create_api(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)

    if not title:
        return JsonResponse({'error': 'Название задачи не указано'}, status=400)

    task = TodoTask.objects.create(title=title, created_by=request.user)
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'status': task.status
    })


@admin_required
@require_http_methods(["POST"])
def todo_update_api(request, task_id):
    try:
        task = TodoTask.objects.get(pk=task_id)
        data = json.loads(request.body.decode('utf-8'))
        if 'status' in data:
            task.status = data['status']
            task.save()
        return JsonResponse({'success': True})
    except TodoTask.DoesNotExist:
        return JsonResponse({'error': 'Задача не найдена'}, status=404)


@admin_required
@require_http_methods(["DELETE"])
def todo_delete_api(request, task_id):
    try:
        TodoTask.objects.get(id=task_id).delete()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False}, status=404)


def home(request):
    offset = int(request.GET.get('offset', 0))
    limit = 9
    addresses = AddressBase.objects.all()

    address_query = request.GET.get('address', '').strip()
    store_id = request.GET.get('store')
    category_id = request.GET.get('category')

    lowest_price = Price.objects.filter(
        product=OuterRef('pk')
    ).order_by('price')

    products_query = Product.objects.annotate(
        min_price=Subquery(lowest_price.values('price')[:1]),
        store_name=Subquery(lowest_price.values('store__name')[:1])
    )

    if category_id:
        products_query = products_query.filter(category_id=category_id)

    if store_id:
        products_query = products_query.filter(
            price__store_id=store_id).distinct()

    if address_query:
        products_query = products_query.filter(
            price__store__address__icontains=address_query
        ).distinct()

    products = products_query.order_by('name')[offset:offset+limit]
    has_more = products_query.order_by(
        'name')[offset+limit:offset+limit+1].exists()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list(
                'product_id', flat=True)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('catalog/includes/product_cards.html', {
            'products': products,
            'favorite_ids': favorite_ids,
        }, request=request)
        return JsonResponse({'html': html, 'has_more': has_more})

    return render(request, 'catalog/home.html', {
        'products': products,
        'favorite_ids': favorite_ids,
        'addresses': addresses,
        'has_more': has_more,
    })


def product_detail(request, pk):
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, pk=pk)
    prices = Price.objects.filter(product=product).select_related('store')
    return render(request, 'catalog/product_detail.html', {'product': product, 'prices': prices})


def get_stores_by_address(request, address_id):
    stores = Store.objects.filter(
        address_base_id=address_id).values('id', 'name')
    return JsonResponse({'stores': list(stores)})


def get_products_by_store(request, store_id):
    lowest_price = Price.objects.filter(
        product=OuterRef('pk'), store_id=store_id
    ).order_by('price')

    products = Product.objects.annotate(
        min_price=Subquery(lowest_price.values('price')[:1]),
        store_name=Subquery(lowest_price.values('store__name')[:1])
    ).filter(price__store_id=store_id).distinct()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(
            user=request.user).values_list('product_id', flat=True))

    html = render_to_string('catalog/includes/product_cards.html', {
        'products': products,
        'favorite_ids': favorite_ids,
    }, request=request)

    return JsonResponse({'html': html})
