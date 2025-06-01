from django import forms
from .models import Price, Product, User, Complaint
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
