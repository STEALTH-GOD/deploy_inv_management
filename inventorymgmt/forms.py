from django import forms
from .models import Stock
from suppliers.models import Supplier


class StockCreateForm(forms.ModelForm):
    supplier_name = forms.CharField(label="Supplier", required=False)
    
    class Meta:
        model = Stock
        fields = ['item_name', 'quantity', 'category', 'brand', 'price', 'reorder_level','supplier_name', 'image','export_to_CSV']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Type supplier name...'
        })
        # If editing an existing stock item, populate supplier_name
        instance = kwargs.get('instance')
        if instance and instance.supplier:
            self.initial['supplier_name'] = instance.supplier.name

    def clean_supplier_name(self):
        name = self.cleaned_data.get('supplier_name', '').strip()
        return name if name else None

    def save(self, commit=True):
        stock = super().save(commit=False)
        supplier_name = self.cleaned_data.get('supplier_name')
        
        if supplier_name:
            supplier, created = Supplier.objects.get_or_create(name=supplier_name)
            stock.supplier = supplier
        else:
            stock.supplier = None
            
        if commit:
            stock.save()
        return stock


class StockSearchForm(forms.ModelForm):
    item_name = forms.CharField(required=False)
    brand = forms.CharField(required=False)
    category = forms.CharField(required=False)
    date_from = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    date_to = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'date'}))

    class Meta:
        model = Stock
        fields = ['item_name', 'brand', 'category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Search by name...'})
        self.fields['brand'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Search by brand...'})
        self.fields['category'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Search by category...'})
        self.fields['date_from'].widget.attrs.update({'class': 'form-control'})
        self.fields['date_to'].widget.attrs.update({'class': 'form-control'})

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity']

class IssueForm(forms.ModelForm):
    class Meta:
        model=Stock
        fields=['issue_quantity']

class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity', 'supplier']

class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model=Stock
        fields=['reorder_level']

