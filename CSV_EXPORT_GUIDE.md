# CSV Export Feature

## ✅ Feature Added!

Export your inventory items to CSV format with one click!

## How to Use

### 1. **Export All Items**

- Go to **List Items** page (`/list_items/`)
- Click the **"Export to CSV"** button (green button with CSV icon)
- File downloads automatically as `inventory_export_YYYYMMDD_HHMMSS.csv`

### 2. **Export Filtered Items** (Optional)

- Apply filters (item name, brand, category)
- Then click **"Export to CSV"**
- Only filtered items will be exported

## What's Exported

The CSV file includes:

- ✅ ID
- ✅ Item Name
- ✅ Quantity
- ✅ Category
- ✅ Brand
- ✅ Price (रु)
- ✅ Reorder Level
- ✅ Supplier Name
- ✅ Supplier Contact
- ✅ Created By
- ✅ Created Date
- ✅ Last Updated

## File Format

```csv
ID,Item Name,Quantity,Category,Brand,Price (रु),Reorder Level,Supplier,Supplier Contact,Created By,Created Date,Last Updated
1,Laptop,50,Electronics,Dell,75000,10,Tech Suppliers,9841234567,admin,2025-12-01 10:30,2025-12-07 14:20
2,Mouse,200,Accessories,Logitech,1500,20,Tech Suppliers,9841234567,admin,2025-12-02 09:15,2025-12-06 11:45
```

## Features

✨ **Automatic Timestamp**: Each export has a unique timestamp in filename
✨ **Supplier Info Included**: Shows supplier name and contact
✨ **Filter Support**: Export only what you need
✨ **Excel Compatible**: Opens directly in Excel/Google Sheets
✨ **UTF-8 Encoded**: Supports Nepali Rupee symbol (रु) and special characters

## Opening the CSV

### In Excel:

1. Download the CSV file
2. Open Excel
3. Go to File → Open
4. Select the downloaded CSV file
5. Data will be properly formatted!

### In Google Sheets:

1. Go to Google Sheets
2. File → Import
3. Upload the CSV file
4. Data imports automatically!

## Tips

💡 **Export Regularly**: Use this to backup your inventory
💡 **Share with Team**: Easy way to share inventory data
💡 **Analyze Data**: Import into Excel for analysis, charts, etc.
💡 **Print Reports**: Export and print for offline reference

## Button Location

The **"Export to CSV"** button is located:

- Page: **List Items** (`/list_items/`)
- Position: Top right, next to "Add New Item" button
- Color: Green with CSV icon

## Examples

### Use Case 1: Full Inventory Backup

1. Go to List Items
2. Don't apply any filters
3. Click "Export to CSV"
4. Result: All inventory items exported

### Use Case 2: Export Low Stock Items

1. Apply filter for items below reorder level (you can add this filter if needed)
2. Click "Export to CSV"
3. Result: Only low stock items exported

### Use Case 3: Export by Category

1. Filter by category (e.g., "Electronics")
2. Click "Export to CSV"
3. Result: Only electronics items exported

## Troubleshooting

### If CSV doesn't download:

1. Check browser's download settings
2. Allow downloads from localhost
3. Try a different browser

### If special characters don't display:

1. Open the CSV in a text editor
2. Save it with UTF-8 encoding
3. Then open in Excel/Sheets

### If you need additional columns:

Edit `inventorymgmt/views.py` in the `export_to_csv` function to add more fields.

## Technical Details

- **URL**: `/export-csv/`
- **Method**: GET
- **Authentication**: Login required
- **Performance**: Optimized with `select_related('supplier')` for fast export
- **File Type**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8

## Future Enhancements (Optional)

You could add:

- Export to Excel (.xlsx) format
- Export to PDF
- Email export to your email
- Scheduled exports (daily/weekly)
- Export history items
- Custom column selection

---

**Ready to use! Just click the green "Export to CSV" button on the List Items page!** 📊
