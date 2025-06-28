from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class PriceAdminForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['product', 'price']

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        self.current_store = kwargs.pop('current_store', None)
        super().__init__(*args, **kwargs)

        if self.current_user and self.current_store:
            used_products = Price.objects.filter(
                store=self.current_store).values_list('product_id', flat=True)
            self.fields['product'].queryset = Product.objects.exclude(
                id__in=used_products)
        else:
            self.fields['product'].queryset = Product.objects.none()


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'category': forms.Select()
        }


class CustomUserCreationForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2')


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['product', 'store', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Опишите проблему'}),
        }


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address_base', 'house_number', 'phone']


class ProductSuggestionForm(forms.ModelForm):
    class Meta:
        model = ProductSuggestion
        fields = ['name', 'category_text', 'manufacturer',
                  'price', 'store_text', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'store': forms.Select(attrs={'class': 'form-select'}),
        }


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        exists = Manufacturer.objects.filter(name__iexact=name)

        # При редактировании — исключаем себя
        if self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise forms.ValidationError(
                "Производитель с таким названием уже существует.")
        return name
