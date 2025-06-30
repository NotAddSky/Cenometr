from django.shortcuts import render, get_object_or_404, redirect
from catalog.models import *
from catalog.forms import *
from catalog.decorators import role_required
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils.timezone import now
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from io import BytesIO
from PIL import Image
from django.template.loader import render_to_string


@role_required('admin')
def product_list(request):
    products = Product.objects.select_related('category', 'manufacturer').all()
    return render(request, 'admin_panel/product_list.html', {'products': products})


@role_required('admin')
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'admin_panel/store_list.html', {'stores': stores})


@role_required('admin')
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'admin_panel/category_list.html', {'categories': categories})


@role_required('admin')
def category_edit(request, pk=None):
    category = get_object_or_404(ProductCategory, pk=pk) if pk else None
    form = ProductAdminForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('admin_category_list')
    return render(request, 'admin_panel/category_form.html', {'form': form})


@role_required('admin')
def store_edit(request, pk=None):
    store = get_object_or_404(Store, pk=pk) if pk else None
    form = StoreForm(request.POST or None, instance=store)
    if form.is_valid():
        form.save()
        return redirect('admin_store_list')
    return render(request, 'admin_panel/store_form.html', {'form': form})


@role_required('admin')
def manufacturer_list(request):
    return render(request, 'admin_panel/manufacturer_list.html')


@role_required('admin')
def dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_stores': Store.objects.count(),
        'pending_suggestions': ProductSuggestion.objects.filter(status='new').count()
    }
    return render(request, 'admin_panel/dashboard.html', context)


class SuggestionModerationForm(forms.ModelForm):
    class Meta:
        model = ProductSuggestion
        fields = ['status', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


@role_required('admin')
def moderate_suggestions(request):
    suggestions = ProductSuggestion.objects.filter(
        status='new').select_related('user').order_by('-created_at')
    return render(request, 'admin_panel/moderate_suggestions.html', {
        'suggestions': suggestions
    })


@role_required('admin')
def suggestion_list(request):
    suggestions = ProductSuggestion.objects.select_related(
        'user').order_by('-created_at')
    return render(request, 'admin_panel/suggestion_list.html', {
        'suggestions': suggestions
    })


@role_required('admin')
def suggestion_detail(request, pk):
    suggestion = get_object_or_404(ProductSuggestion, pk=pk)
    form = SuggestionModerationForm(request.POST or None, instance=suggestion)

    if request.method == 'POST' and form.is_valid():
        suggestion = form.save(commit=False)
        suggestion.reviewed_at = now()
        suggestion.save()
        messages.success(request, 'Предложение обновлено.')
        return redirect('admin_moderate_suggestions')

    return render(request, 'admin_panel/suggestion_detail.html', {
        'suggestion': suggestion,
        'form': form
    })


@csrf_exempt
@role_required('user')
@require_POST
def suggest_product_api(request):
    name = request.POST.get("name", "").strip()
    category = request.POST.get("category", "").strip()
    manufacturer = request.POST.get("manufacturer", "").strip()
    store = request.POST.get("store", "").strip()
    price = request.POST.get("price")
    image_file = request.FILES.get("image")

    if not name or not category or not store or not price:
        return JsonResponse({'success': False, 'error': 'Заполните все обязательные поля'})

    suggestion = ProductSuggestion.objects.create(
        user=request.user,
        name=name,
        manufacturer=manufacturer,
        category_text=category,
        store_text=store,
        price=price
    )

    if image_file:
        try:
            img = Image.open(image_file)
            img_io = BytesIO()
            img.save(img_io, format="WEBP", lossless=True)
            img_content = ContentFile(
                img_io.getvalue(), f"{suggestion.id}.webp")
            suggestion.image.save(
                f"suggestion_{suggestion.id}.webp", img_content)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Ошибка обработки изображения'})

    suggestion.save()
    return JsonResponse({'success': True})


@role_required('admin')
@require_POST
def approve_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(ProductSuggestion, id=suggestion_id)
    suggestion.status = 'approved'
    suggestion.reviewed_at = now()

    manufacturer = None
    if suggestion.manufacturer:
        manufacturer, _ = Manufacturer.objects.get_or_create(
            name=suggestion.manufacturer)

    product = Product.objects.create(
        name=suggestion.name,
        category=suggestion.category,
        manufacturer=manufacturer,
        quantity_value=1,
        quantity_unit='pcs'
    )

    Price.objects.create(
        product=product,
        store=suggestion.store,
        price=suggestion.price
    )

    suggestion.save()
    return redirect('admin_moderate_suggestions')


@role_required('admin')
@require_POST
def reject_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(ProductSuggestion, id=suggestion_id)
    suggestion.status = 'rejected'
    suggestion.reviewed_at = now()
    suggestion.admin_comment = request.POST.get('admin_comment', '')
    suggestion.save()
    return redirect('admin_moderate_suggestions')


@role_required('admin')
def manufacturer_list(request):
    manufacturers = Manufacturer.objects.annotate(
        product_count=Count('product'))
    return render(request, 'admin_panel/manufacturer_list.html', {
        'manufacturers': manufacturers
    })


@role_required('admin')
@require_POST
def add_manufacturer(request):
    name = request.POST.get('name', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': 'Название не может быть пустым.'})

    if Manufacturer.objects.filter(name__iexact=name).exists():
        return JsonResponse({'success': False, 'error': 'Производитель с таким названием уже существует.'})

    manufacturer = Manufacturer.objects.create(name=name)
    return JsonResponse({
        'success': True,
        'id': manufacturer.id,
        'name': manufacturer.name
    })


@role_required('admin')
@require_POST
def edit_manufacturer(request, manufacturer_id):
    name = request.POST.get('name', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': 'Название не может быть пустым.'})

    if Manufacturer.objects.filter(name__iexact=name).exclude(id=manufacturer_id).exists():
        return JsonResponse({'success': False, 'error': 'Производитель с таким названием уже существует.'})

    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
    manufacturer.name = name
    manufacturer.save()

    return JsonResponse({'success': True, 'name': manufacturer.name})


@role_required('admin')
@require_POST
def delete_manufacturer(request, manufacturer_id):
    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)

    if Product.objects.filter(manufacturer=manufacturer).exists():
        return JsonResponse({
            'success': False,
            'error': f'Нельзя удалить. Производитель используется в одном или нескольких товарах.'
        })

    manufacturer.delete()
    return JsonResponse({'success': True})


@role_required('admin')
def product_management(request):
    products = Product.objects.select_related(
        'category', 'manufacturer').all()[:200]
    categories = ProductCategory.objects.all()
    manufacturers = Manufacturer.objects.all()

    return render(request, 'admin_panel/product_management.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    })


@role_required('admin')
def product_management(request):
    return render(request, 'admin_panel/product_management.html')


@role_required('admin')
def fetch_products(request):
    from catalog.models import Product
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 20

    products = Product.objects.select_related('category', 'manufacturer')
    if query:
        products = products.filter(name__icontains=query)

    total = products.count()
    products = products[(page-1)*per_page: page*per_page]

    return render(request, 'admin_panel/includes/products_table.html', {
        'products': products,
        'page': page,
        'total': total,
        'per_page': per_page,
    })


@role_required('admin')
def fetch_categories(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 20

    categories = ProductCategory.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)

    total = categories.count()
    categories = categories[(page - 1) * per_page: page * per_page]

    return render(request, 'admin_panel/includes/categories_table.html', {
        'categories': categories,
        'page': page,
        'total': total,
        'per_page': per_page,
    })


@role_required('admin')
def fetch_manufacturers(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    per_page = 20

    manufacturers = Manufacturer.objects.all()
    if query:
        manufacturers = manufacturers.filter(name__icontains=query)

    total = manufacturers.count()
    manufacturers = manufacturers[(page - 1) * per_page: page * per_page]

    return render(request, 'admin_panel/includes/manufacturers_table.html', {
        'manufacturers': manufacturers,
        'page': page,
        'total': total,
        'per_page': per_page,
    })


@require_POST
def save_product(request):
    try:
        product_id = request.POST.get('id')
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        manufacturer_id = request.POST.get('manufacturer')

        if not name or not category_id:
            return JsonResponse({'error': 'Название и категория обязательны.'})

        category = ProductCategory.objects.get(id=category_id)
        manufacturer = Manufacturer.objects.filter(
            id=manufacturer_id).first() if manufacturer_id else None

        if product_id:
            product = Product.objects.get(id=product_id)
            product.name = name
            product.category = category
            product.manufacturer = manufacturer
            product.save()
        else:
            Product.objects.create(
                name=name, category=category, manufacturer=manufacturer)

        return JsonResponse({'success': True})

    except ProductCategory.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Товар не найден'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def save_category(request):
    try:
        category_id = request.POST.get('id')
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'error': 'Название обязательно'})

        if ProductCategory.objects.exclude(id=category_id).filter(name__iexact=name).exists():
            return JsonResponse({'error': 'Категория с таким названием уже существует'})

        if category_id:
            category = ProductCategory.objects.get(id=category_id)
            category.name = name
            category.save()
        else:
            ProductCategory.objects.create(name=name)

        return JsonResponse({'success': True})
    except ProductCategory.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_POST
def save_manufacturer(request):
    try:
        manufacturer_id = request.POST.get('id')
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'error': 'Название обязательно'})

        if Manufacturer.objects.exclude(id=manufacturer_id).filter(name__iexact=name).exists():
            return JsonResponse({'error': 'Производитель с таким названием уже существует'})

        if manufacturer_id:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            manufacturer.name = name
            manufacturer.save()
        else:
            Manufacturer.objects.create(name=name)

        return JsonResponse({'success': True})
    except Manufacturer.DoesNotExist:
        return JsonResponse({'error': 'Производитель не найден'})
    except Exception as e:
        return JsonResponse({'error': str(e)})
