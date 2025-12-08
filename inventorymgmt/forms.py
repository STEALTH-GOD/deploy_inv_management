from django import forms
from .models import Stock, Sale
from suppliers.models import Supplier
import uuid
import logging

# Conditional import to avoid errors if supabase not installed
try:
    from .supabase_storage import SupabaseStorage
except ImportError:
    SupabaseStorage = None

logger = logging.getLogger(__name__)


class StockCreateForm(forms.ModelForm):
    supplier_name = forms.CharField(label="Supplier", required=False)
    # Use CharField for image field in form (we'll handle upload separately)
    image = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*',
        'id': 'image-input'
    }))
    
    class Meta:
        model = Stock
        fields = ['item_name', 'quantity', 'category', 'brand', 'price', 'reorder_level','supplier_name', 'export_to_CSV']
    
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

    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file is too large. Max size is 5MB.")
            
            # Validate image format by checking content type
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image

    def save(self, commit=True):
        # Save without image first (since it's not in fields)
        stock = super().save(commit=False)
        supplier_name = self.cleaned_data.get('supplier_name')
        image_file = self.cleaned_data.get('image')
        
        # Handle Supabase image upload
        if image_file:
            try:
                print(f"\n🔄 Processing image upload in form...")
                supabase = SupabaseStorage()
                
                # Generate unique filename
                filename = f"product_{uuid.uuid4()}_{image_file.name}"
                print(f"  Generated filename: {filename}")
                
                # Upload to Supabase and get public URL
                image_url = supabase.upload_image(image_file, filename)
                
                if image_url:
                    stock.image = image_url
                    print(f"  ✅ Image URL saved to model: {image_url}\n")
                else:
                    print(f"  ❌ Upload returned None\n")
                    raise forms.ValidationError("Failed to upload image to Supabase. Please try again.")
            except forms.ValidationError:
                raise
            except Exception as e:
                print(f"  ❌ Exception during upload: {str(e)}\n")
                raise forms.ValidationError(f"Error uploading image: {str(e)}")
        else:
            print(f"  ℹ️ No image provided")
            stock.image = None
        
        if supplier_name:
            supplier, created = Supplier.objects.get_or_create(name=supplier_name)
            stock.supplier = supplier
        else:
            stock.supplier = None
            
        if commit:
            stock.save()
            print(f"  ✅ Stock saved to database with image URL\n")
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


class SaleForm(forms.ModelForm):
	"""Form to add a new sale"""
	class Meta:
		model = Sale
		fields = ['stock', 'quantity_sold', 'selling_price']
		widgets = {
			'stock': forms.Select(attrs={
				'class': 'form-control',
				'id': 'stock-select'
			}),
			'quantity_sold': forms.NumberInput(attrs={
				'class': 'form-control',
				'type': 'number',
				'min': '1',
				'placeholder': 'Enter quantity',
				'id': 'quantity-input'
			}),
			'selling_price': forms.NumberInput(attrs={
				'class': 'form-control',
				'type': 'number',
				'step': '0.01',
				'placeholder': 'Enter selling price',
				'id': 'price-input'
			})
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Only show items with quantity > 0
		self.fields['stock'].queryset = Stock.objects.filter(quantity__gt=0).order_by('item_name')
		self.fields['stock'].label = 'Product'
		self.fields['quantity_sold'].label = 'Quantity'
		self.fields['selling_price'].label = 'Selling Price'
	
	def clean(self):
		cleaned_data = super().clean()
		stock = cleaned_data.get('stock')
		quantity = cleaned_data.get('quantity_sold')
		
		if stock and quantity and quantity > stock.quantity:
			raise forms.ValidationError(f"Only {stock.quantity} items in stock!")
		
		return cleaned_data


class SaleFilterForm(forms.Form):
	"""Form to filter sales by date and item"""
	item_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': 'Search item name...'
	}))
	date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
		'class': 'form-control',
		'type': 'date'
	}))
	date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
		'class': 'form-control',
		'type': 'date'
	}))
