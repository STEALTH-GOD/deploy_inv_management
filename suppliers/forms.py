from django import forms
from .models import Supplier, Brand

class SupplierForm(forms.ModelForm):
    brand_names = forms.CharField(
        label="Brands", 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Samsung, Apple, Sony'})
    )

    class Meta:
        model = Supplier
        fields = ['name', 'phone_number', 'email', 'address']  # Remove 'brands' from here
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        # If editing an existing supplier, populate brand_names with existing brands
        if instance:
            self.initial['brand_names'] = ', '.join(brand.name for brand in instance.brands.all())

    def save(self, commit=True):
        supplier = super().save(commit=False)
        if commit:
            supplier.save()
            # Handle brands - clear existing and add new ones
            brand_names = self.cleaned_data.get('brand_names', '')
            if brand_names:
                brand_list = [name.strip() for name in brand_names.split(',') if name.strip()]
                brands = []
                for name in brand_list:
                    brand, created = Brand.objects.get_or_create(name=name)
                    brands.append(brand)
                supplier.brands.set(brands)
            else:
                supplier.brands.clear()
        return supplier