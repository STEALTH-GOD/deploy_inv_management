from django.db import models
import os
from django.dispatch import receiver
from django.contrib.auth.models import User
from suppliers.models import Supplier
from .utils import compress_image

# Supabase import (conditional to avoid import errors during development)
try:
    from .supabase_storage import SupabaseStorage
except ImportError:
    SupabaseStorage = None

class Stock(models.Model):
	item_name = models.CharField(max_length=50, blank=False, null=False, db_index=True)
	quantity = models.IntegerField(default='0', blank=False, null=False)
	category = models.CharField(max_length=50, blank=True, null=True, db_index=True)
	brand = models.CharField(max_length=50,  blank=True, null=True, db_index=True)
	price = models.CharField(max_length=10, blank=False, null=True)
	receive_quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_by = models.CharField(max_length=50, blank=True, null=True)
	issue_quantity = models.IntegerField(default='0', blank=True, null=True)
	issue_by = models.CharField(max_length=50, blank=True, null=True)
	issue_to = models.CharField(max_length=50, blank=True, null=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	reorder_level = models.IntegerField(default='0', blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	image = models.URLField(max_length=500, blank=True, null=True, help_text="Supabase CDN URL for product image")
	export_to_CSV = models.BooleanField(default=False)
	supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='stocks')
	added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='added_stocks', help_text="User who added this stock item")
	
	class Meta: 
		constraints = [
			models.UniqueConstraint(
				fields=['item_name', 'brand', 'category'],
				name='unique_stock'
			)
		]
	
	def __str__(self):
		return self.item_name


class StockHistory(models.Model):
    stock_id = models.IntegerField(blank=True, null=True)  
    item_name = models.CharField(max_length=50,blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    price = models.CharField(max_length=10, blank=True, null=True)
    receive_quantity = models.IntegerField(blank=True, null=True)
    receive_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(blank=True, null=True)
    issue_by = models.CharField(max_length=50, blank=True, null=True)
    issue_to = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    reorder_level = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='stock_histories')





def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes image from Supabase when corresponding `Stock` object is deleted.
    """
    if instance.image and SupabaseStorage:
        # Extract filename from Supabase URL
        try:
            supabase = SupabaseStorage()
            # Get filename from URL (last part after /)
            filename = instance.image.split('/')[-1]
            supabase.delete_image(filename)
        except Exception as e:
            print(f"Error deleting image from Supabase: {e}")

# Connect the function to post_delete signal
@receiver(models.signals.post_delete, sender=Stock)
def auto_delete_file_on_delete_handler(sender, instance, **kwargs):
    auto_delete_file_on_delete(sender, instance, **kwargs)

# 🚨 Replace old image when a new one is uploaded
@receiver(models.signals.pre_save, sender=Stock)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from Supabase when `Stock` object is updated with new file.
    """
    if not instance.pk or not SupabaseStorage:
        return False

    try:
        old_instance = Stock.objects.get(pk=instance.pk)
        old_image = old_instance.image
    except Stock.DoesNotExist:
        return False

    new_image = instance.image
    if old_image and old_image != new_image:
        try:
            supabase = SupabaseStorage()
            # Get filename from Supabase URL
            filename = old_image.split('/')[-1]
            supabase.delete_image(filename)
        except Exception as e:
            print(f"Error deleting old image from Supabase: {e}")

class Sale(models.Model):
	"""Model to track individual sales transactions"""
	stock = models.ForeignKey(Stock, on_delete=models.SET_NULL,null=True,blank=True, related_name='sales')
	quantity_sold = models.IntegerField(default=1, blank=False, null=False)
	selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
	subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
	sold_by = models.CharField(max_length=50, blank=True, null=True)
	sale_date = models.DateTimeField(auto_now_add=True)
    
	
	class Meta:
		ordering = ['-sale_date']
		indexes = [
			models.Index(fields=['-sale_date']),
			models.Index(fields=['stock']),
		]
	
	def __str__(self):
		return f"{self.stock.item_name} x {self.quantity_sold} on {self.sale_date.strftime('%Y-%m-%d %H:%M')}"
	
	def save(self, *args, **kwargs):
		"""Calculate subtotal and update stock"""
		if not self.subtotal:
			self.subtotal = self.quantity_sold * self.selling_price
		
		# Check if this is a new sale (not updating existing)
		if not self.pk:
			# Auto-update stock when sale is created
			self.stock.quantity -= self.quantity_sold
			self.stock.save()
		
		super().save(*args, **kwargs)