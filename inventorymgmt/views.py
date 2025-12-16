from django.shortcuts import render,redirect, get_object_or_404
from .models import Stock, StockHistory, Sale
from .forms import * 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, F, DecimalField
from django.db.models.functions import Cast
import csv
from datetime import datetime, date, timedelta
from decimal import Decimal
# Create your views here.

@login_required
def home(request):
    return render(request, 'inventory/home.html')

@login_required
def list_items(request):
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.select_related('supplier').all()
    
    if request.method == 'POST' and form.is_valid():
        item_name = form.cleaned_data.get('item_name')
        brand = form.cleaned_data.get('brand')
        category = form.cleaned_data.get('category')
        
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        if category:
            queryset = queryset.filter(category__icontains=category)
    
    # Order by item name to avoid pagination warning
    queryset = queryset.order_by('item_name')
    
    # pagination
    paginator = Paginator(queryset, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'queryset': page_obj,  # Use page_obj instead of queryset
        'title': 'Inventory Items'
    }
    return render(request, 'inventory/list_items.html', context)

# def add_items(request):
#     form = StockCreateForm(request.method == "POST")
#     if form.is_valid():
#         form.save()
#     context={
#         "form": form,
#         "title": "Add Item"
#     }
#     return render(request, 'inventory/add_items.html',context)


@login_required
def add_items(request):
    if request.method == "POST":
        form = StockCreateForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.added_by = request.user  # Set the user who added this item
            item.save()
            
            # Create history record for item creation
            StockHistory.objects.create(
                stock_id=item.id,
                item_name=item.item_name,
                quantity=item.quantity,
                category=item.category,
                brand=item.brand,
                price=item.price,
                created_by=request.user.username,
                supplier=item.supplier,
                last_updated=item.last_updated,
                timestamp=item.last_updated
            )
            
            messages.success(request, f'{item.item_name} has been added successfully')
            return redirect('list_items')
        else:
            print("\n❌ FORM VALIDATION FAILED:")
            print(f"Form errors: {form.errors}")
            print(f"Non-field errors: {form.non_field_errors()}")
    else:
        form = StockCreateForm()
    
    context = {
        'form': form,
        'title': 'Add Item'
    }
    return render(request, 'inventory/add_items.html', context)

@login_required
def update_items(request, pk):
    item = Stock.objects.get(id=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=item)
        if form.is_valid():
            changed_fields = form.changed_data  
            updated_item = form.save()

            if changed_fields:
                for field in changed_fields:
                    messages.success(
                        request,
                        f"{field.replace('_', ' ').title()} has been updated successfully"
                    )
            else:
                messages.info(request, "No changes were made")

            return redirect('list_items')
    else:
        form = StockUpdateForm(instance=item)
    
    context = {
        'form': form,
        'title': f'Update {item.item_name}'
    }
    return render(request, 'inventory/update_items.html', context)

@login_required
def delete_items(request, pk):
    item = get_object_or_404(Stock, id=pk)
    if request.method == 'POST':
        item.delete()
        messages.warning(request, f'{item.item_name} has been deleted successfully')
        return redirect('list_items')
    context = {
        'item': item
    }
    return render(request, 'inventory/delete_items.html', context)

@login_required
def stock_details(request, pk):
    stock = get_object_or_404(Stock, id=pk)   
    return render(request, 'inventory/stock_details.html', {'stock': stock})

@login_required
def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.receive_quantity = 0
        old_issue_quantity = instance.issue_quantity
        instance.quantity -= old_issue_quantity
        
        # Create history record
        StockHistory.objects.create(
            stock_id=instance.id,
            item_name=instance.item_name,
            quantity=instance.quantity,
            category=instance.category,
            brand=instance.brand,
            price=instance.price,
            issue_quantity=old_issue_quantity,
            issue_by=request.user.username,
            issue_to=form.cleaned_data.get('issue_to', ''),
            supplier=instance.supplier,
            last_updated=instance.last_updated,
            timestamp=instance.last_updated
        )
        
        messages.success(request, f"Issued SUCCESSFULLY. {instance.quantity} {instance.item_name}s now left in Store")
        instance.save()
        return redirect(f'/stock_details/{instance.id}')
    
    context = {
        "title": f"Issue {queryset.item_name}",
        "queryset": queryset,
        "form": form,
        "username": "Issue",
        "is_issue_form": True
    }
    return render(request, 'inventory/issue_receive_items.html', context)


@login_required
def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.issue_quantity = 0
        old_receive_quantity = instance.receive_quantity
        instance.quantity += old_receive_quantity
        
        # Create history record
        StockHistory.objects.create(
            stock_id=instance.id,
            item_name=instance.item_name,
            quantity=instance.quantity,
            category=instance.category,
            brand=instance.brand,
            price=instance.price,
            receive_quantity=old_receive_quantity,
            receive_by=request.user.username,
            supplier=instance.supplier,
            last_updated=instance.last_updated,
            timestamp=instance.last_updated
        )
        
        messages.success(request, f"Received Successfully. {instance.quantity} {instance.item_name}s now in Store")
        instance.save()
        return redirect(f'/stock_details/{instance.id}')

    context = {
        "title": f"Receive {queryset.item_name}",
        "queryset": queryset,
        "form": form,
        "username": "Receive",
        "is_receive_form": True
    }
    return render(request, 'inventory/issue_receive_items.html', context)  


@login_required
def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form= ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Reorder Level has been set to " + str(instance.reorder_level) + " for " + str(instance.item_name))
        return redirect('/stock_details/' + str(instance.id))

    
    context = {
        "instance" : queryset,
        "form": form,
        "title": f"Change Reorder Level for {queryset.item_name}",
        "is_reorder_form": True,
        "queryset": queryset,
    }
    return render(request, 'inventory/issue_receive_items.html', context)

    
@login_required
def list_history(request):
    form = StockSearchForm(request.POST or None)
    queryset = StockHistory.objects.select_related('supplier').all()
    
    if request.method == 'POST' and form.is_valid():
        item_name = form.cleaned_data.get('item_name')
        brand = form.cleaned_data.get('brand')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if date_from:
            queryset = queryset.filter(last_updated__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(last_updated__date__lte=date_to)
    
    # Order by most recent first
    queryset = queryset.order_by('-last_updated')
    
    #pagination
    paginator = Paginator(queryset, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'queryset': page_obj,  
        'title': 'Inventory History'
    }
    return render(request, 'inventory/list_history.html', context)

@login_required
def delete_history(request, pk):
    history = get_object_or_404(StockHistory, pk=pk)
    if request.method == "POST":
        history.delete()
        messages.success(request, "History entry deleted successfully.")
    return redirect('list_history')

@login_required
def bulk_delete_history(request):
    """Delete multiple history entries at once"""
    if request.method == "POST":
        history_ids = request.POST.getlist('history_ids')
        if history_ids:
            deleted_count = StockHistory.objects.filter(id__in=history_ids).delete()[0]
            messages.success(request, f"{deleted_count} history entries deleted successfully.")
        else:
            messages.warning(request, "No items selected for deletion.")
    return redirect('list_history')

@login_required
def export_to_csv(request):
    """Export all stock items to CSV file"""
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="inventory_export_{timestamp}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'ID',
        'Item Name',
        'Quantity',
        'Category',
        'Brand',
        'Price (रु)',
        'Reorder Level',
        'Supplier',
        'Supplier Contact',
        'Created By',
        'Created Date',
        'Last Updated'
    ])
    
    # Get stock items (all or filtered)
    stocks = Stock.objects.select_related('supplier').all()
    
    # Apply filters if provided in GET parameters
    item_name = request.GET.get('item_name')
    brand = request.GET.get('brand')
    category = request.GET.get('category')
    
    if item_name:
        stocks = stocks.filter(item_name__icontains=item_name)
    if brand:
        stocks = stocks.filter(brand__icontains=brand)
    if category:
        stocks = stocks.filter(category__icontains=category)
    
    stocks = stocks.order_by('item_name')
    
    # Write data rows
    for stock in stocks:
        writer.writerow([
            stock.id,
            stock.item_name,
            stock.quantity,
            stock.category or 'N/A',
            stock.brand or 'N/A',
            stock.price or '0',
            stock.reorder_level or '0',
            stock.supplier.name if stock.supplier else 'N/A',
            stock.supplier.phone_number if stock.supplier else 'N/A',
            stock.created_by or 'N/A',
            stock.timestamp.strftime('%Y-%m-%d %H:%M') if stock.timestamp else 'N/A',
            stock.last_updated.strftime('%Y-%m-%d %H:%M') if stock.last_updated else 'N/A'
        ])
    
    return response


# ==================== SALES/POS VIEWS ====================

@login_required
def pos_page(request):
	"""Main POS page for selling items"""
	# Get search and filter parameters
	search_query = request.GET.get('search', '').strip()
	category_filter = request.GET.get('category', '').strip()
	
	# Get all items in stock
	items = Stock.objects.filter(quantity__gt=0).select_related('supplier')
	
	# Apply filters
	if search_query:
		items = items.filter(
			Q(item_name__icontains=search_query) |
			Q(brand__icontains=search_query)
		)
	
	if category_filter:
		items = items.filter(category__icontains=category_filter)
	
	items = items.order_by('item_name')
	
	# Get unique categories for filter dropdown
	categories = Stock.objects.filter(quantity__gt=0).values_list('category', flat=True).distinct()
	categories = sorted([c for c in categories if c])
	
	# Get today's sales
	today = date.today()
	today_sales = Sale.objects.filter(
		sale_date__date=today
	).select_related('stock').order_by('-sale_date')
	
	# Calculate today's totals
	today_total = today_sales.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
	today_quantity = today_sales.aggregate(qty=Sum('quantity_sold'))['qty'] or 0
	
	# Paginate today's sales
	paginator = Paginator(today_sales, 15)
	page_number = request.GET.get('page')
	sales_page = paginator.get_page(page_number)
	
	context = {
		'items': items,
		'categories': categories,
		'search_query': search_query,
		'category_filter': category_filter,
		'sales_today': sales_page,
		'today_total': today_total,
		'today_quantity': today_quantity,
		'form': SaleForm(),
	}
	return render(request, 'inventory/pos_page.html', context)


@login_required
def add_sale(request):
	"""Add a new sale (AJAX request)"""
	if request.method == 'POST':
		form = SaleForm(request.POST)
		if form.is_valid():
			sale = form.save(commit=False)
			sale.sold_by = request.user.username
			sale.save()
			
			return JsonResponse({
				'status': 'success',
				'message': f'Sale added successfully!',
				'sale_id': sale.id,
				'item_name': sale.stock.item_name,
				'quantity': sale.quantity_sold,
				'price': str(sale.selling_price),
				'subtotal': str(sale.subtotal),
				'timestamp': sale.sale_date.strftime('%Y-%m-%d %H:%M:%S')
			})
		else:
			errors = form.errors.as_json()
			return JsonResponse({'status': 'error', 'errors': errors}, status=400)
	
	return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def get_product_price(request, product_id):
	"""Get product price via AJAX"""
	try:
		stock = Stock.objects.get(id=product_id)
		return JsonResponse({
			'status': 'success',
			'price': str(stock.price),
			'quantity': stock.quantity,
			'item_name': stock.item_name
		})
	except Stock.DoesNotExist:
		return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)


@login_required
def sales_list(request):
	"""View all sales with filters"""
	form = SaleFilterForm(request.GET or None)
	sales = Sale.objects.select_related('stock').all()
	
	# Apply filters
	if request.GET:
		item_name = request.GET.get('item_name', '').strip()
		date_from = request.GET.get('date_from')
		date_to = request.GET.get('date_to')
		
		if item_name:
			sales = sales.filter(stock__item_name__icontains=item_name)
		
		if date_from:
			sales = sales.filter(sale_date__date__gte=date_from)
		
		if date_to:
			sales = sales.filter(sale_date__date__lte=date_to)
	
	sales = sales.order_by('-sale_date')
	
	# Pagination
	paginator = Paginator(sales, 25)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	# Calculate totals
	total_sales = sales.aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
	total_quantity = sales.aggregate(qty=Sum('quantity_sold'))['qty'] or 0
	
	context = {
		'form': form,
		'sales': page_obj,
		'total_sales': total_sales,
		'total_quantity': total_quantity,
		'title': 'Sales List'
	}
	return render(request, 'inventory/sales_list.html', context)


@login_required
def delete_sale(request, pk):
	"""Delete a sale and restore stock"""
	sale = get_object_or_404(Sale, id=pk)
	
	if request.method == 'POST':
		# Restore stock if it exists (handle SET_NULL case)
		if sale.stock:
			sale.stock.quantity += sale.quantity_sold
			sale.stock.save()
		
		# Delete sale
		sale.delete()
		messages.warning(request, 'Sale deleted and stock restored.')
		return redirect('pos_page')
	
	context = {'sale': sale}
	return render(request, 'inventory/delete_sale.html', context)
