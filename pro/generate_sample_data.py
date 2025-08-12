import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

def generate_sample_data():
    """Generate comprehensive sample data for procurement analytics with 100+ records."""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate 100 purchase orders
    purchase_orders = generate_purchase_orders(100)
    
    # Generate supporting data
    suppliers = generate_suppliers(20)
    items = generate_items(25)
    deliveries = generate_deliveries(purchase_orders, 100)
    invoices = generate_invoices(purchase_orders, 100)
    contracts = generate_contracts(suppliers, 15)
    budgets = generate_budgets(10)
    rfqs = generate_rfqs(suppliers, items, 30)
    
    # Create Excel file with all sheets
    with pd.ExcelWriter('pro.xlsx', engine='openpyxl') as writer:
        purchase_orders.to_excel(writer, sheet_name='purchase_orders', index=False)
        suppliers.to_excel(writer, sheet_name='suppliers', index=False)
        items.to_excel(writer, sheet_name='items', index=False)
        deliveries.to_excel(writer, sheet_name='deliveries', index=False)
        invoices.to_excel(writer, sheet_name='invoices', index=False)
        contracts.to_excel(writer, sheet_name='contracts', index=False)
        budgets.to_excel(writer, sheet_name='budgets', index=False)
        rfqs.to_excel(writer, sheet_name='rfqs', index=False)
    
    print("✅ Generated comprehensive sample data with 100+ records")
    print(f"📊 Purchase Orders: {len(purchase_orders)} records")
    print(f"🏢 Suppliers: {len(suppliers)} records")
    print(f"📦 Items: {len(items)} records")
    print(f"🚚 Deliveries: {len(deliveries)} records")
    print(f"💰 Invoices: {len(invoices)} records")
    print(f"📋 Contracts: {len(contracts)} records")
    print(f"💼 Budgets: {len(budgets)} records")
    print(f"📝 RFQs: {len(rfqs)} records")
    
    return purchase_orders, suppliers, items, deliveries, invoices, contracts, budgets, rfqs

def generate_purchase_orders(n_records):
    """Generate purchase orders with realistic data."""
    
    departments = ['IT', 'HR', 'Finance', 'Operations', 'Marketing', 'Sales', 'Legal', 'Facilities']
    statuses = ['Open', 'In Progress', 'Completed', 'Cancelled']
    priorities = ['High', 'Medium', 'Low']
    approval_statuses = ['Approved', 'Pending', 'Rejected', 'Under Review']
    currencies = ['USD', 'EUR', 'GBP']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_records):
        order_date = start_date + timedelta(days=random.randint(0, 365))
        delivery_date = order_date + timedelta(days=random.randint(7, 60))
        
        quantity = random.randint(1, 100)
        unit_price = round(random.uniform(10, 1000), 2)
        total_amount = quantity * unit_price
        
        data.append({
            'po_id': f'PO-{str(i+1).zfill(4)}',
            'order_date': order_date,
            'department': random.choice(departments),
            'supplier_id': f'SUP-{random.randint(1, 20)}',
            'item_id': f'ITEM-{random.randint(1, 25)}',
            'quantity': quantity,
            'unit_price': unit_price,
            'delivery_date': delivery_date,
            'currency': random.choice(currencies),
            'budget_code': f'BUD-{random.randint(1, 10)}',
            'total_amount': total_amount,
            'status': random.choice(statuses),
            'priority': random.choice(priorities),
            'approval_status': random.choice(approval_statuses)
        })
    
    return pd.DataFrame(data)

def generate_suppliers(n_suppliers):
    """Generate supplier data."""
    
    countries = ['USA', 'Germany', 'China', 'Japan', 'UK', 'France', 'Canada', 'Australia']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Africa']
    payment_terms = ['Net 30', 'Net 45', 'Net 60']
    certifications = ['ISO 9001', 'ISO 14001', 'OHSAS 18001', 'ISO 27001']
    
    supplier_names = [
        'TechCorp Solutions', 'Global Manufacturing Inc', 'Quality Supplies Co',
        'Innovation Systems', 'Reliable Partners Ltd', 'Advanced Technologies',
        'Premium Components', 'Smart Solutions Group', 'Elite Suppliers',
        'Future Tech Industries', 'Reliable Manufacturing', 'Quality Systems',
        'Innovation Partners', 'Global Tech Solutions', 'Premium Suppliers',
        'Advanced Manufacturing', 'Smart Components', 'Elite Technologies',
        'Future Systems', 'Reliable Tech'
    ]
    
    data = []
    for i in range(n_suppliers):
        registration_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1000))
        
        data.append({
            'supplier_id': f'SUP-{i+1}',
            'supplier_name': supplier_names[i],
            'country': random.choice(countries),
            'region': random.choice(regions),
            'registration_date': registration_date,
            'diversity_flag': random.choice(['Yes', 'No']),
            'esg_score': round(random.uniform(50, 95), 1),
            'certifications': ', '.join(random.sample(certifications, random.randint(1, 3))),
            'risk_score': round(random.uniform(10, 80), 1),
            'city': f'City-{i+1}',
            'contact_person': f'Contact-{i+1}',
            'email': f'contact{i+1}@supplier{i+1}.com',
            'phone': f'+1-555-{str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}',
            'payment_terms': random.choice(payment_terms),
            'certification_status': random.choice(certifications),
            'lead_time_days': random.randint(5, 45)
        })
    
    return pd.DataFrame(data)

def generate_items(n_items):
    """Generate item catalog data."""
    
    categories = ['Electronics', 'Office Supplies', 'Furniture', 'Software', 'Services', 'Equipment']
    units = ['Piece', 'Box', 'Set', 'License', 'Hour', 'Unit']
    subcategories = ['Premium', 'Standard', 'Economy']
    
    item_names = [
        'Laptop Computer', 'Office Chair', 'Printer', 'Software License', 'Desk Lamp',
        'Filing Cabinet', 'Coffee Machine', 'Projector', 'Whiteboard', 'Telephone',
        'Scanner', 'Monitor', 'Keyboard', 'Mouse', 'Headphones', 'Microphone',
        'Webcam', 'Tablet', 'Smartphone', 'Server', 'Network Switch', 'Router',
        'Backup System', 'Security Camera', 'Access Control System'
    ]
    
    data = []
    for i in range(n_items):
        data.append({
            'item_id': f'ITEM-{i+1}',
            'item_name': item_names[i],
            'category': random.choice(categories),
            'unit': random.choice(units),
            'recyclable_flag': random.choice(['Yes', 'No']),
            'carbon_score': round(random.uniform(1, 10), 1),
            'unit_price': round(random.uniform(50, 2000), 2),
            'subcategory': random.choice(subcategories),
            'sustainability_rating': random.randint(1, 5),
            'supplier_id': f'SUP-{random.randint(1, 20)}',
            'min_order_quantity': random.randint(1, 10),
            'lead_time_days': random.randint(3, 30)
        })
    
    return pd.DataFrame(data)

def generate_deliveries(purchase_orders, n_deliveries):
    """Generate delivery data."""
    
    carriers = ['FedEx', 'UPS', 'DHL', 'USPS']
    delivery_statuses = ['Delivered', 'In Transit', 'Out for Delivery']
    
    data = []
    for i in range(n_deliveries):
        po = purchase_orders.iloc[i % len(purchase_orders)]
        expected_date = po['delivery_date']
        actual_date = expected_date + timedelta(days=random.randint(-5, 10))
        
        delivered_quantity = po['quantity']
        if random.random() < 0.1:  # 10% chance of partial delivery
            delivered_quantity = int(delivered_quantity * random.uniform(0.8, 1.0))
        
        on_time = actual_date <= expected_date
        defect_flag = random.random() < 0.05  # 5% defect rate
        
        data.append({
            'delivery_id': f'DEL-{str(i+1).zfill(4)}',
            'po_id': po['po_id'],
            'delivery_date_actual': actual_date,
            'delivered_quantity': delivered_quantity,
            'defect_flag': defect_flag,
            'defect_notes': 'Minor damage' if defect_flag else '',
            'quantity_delivered': delivered_quantity,
            'quality_score': round(random.uniform(70, 100), 1),
            'delivery_date': expected_date,
            'on_time_flag': on_time,
            'carrier': random.choice(carriers),
            'tracking_number': f'TRK{random.randint(100000, 999999)}',
            'delivery_status': 'Delivered' if actual_date <= datetime.now() else random.choice(delivery_statuses)
        })
    
    return pd.DataFrame(data)

def generate_invoices(purchase_orders, n_invoices):
    """Generate invoice data."""
    
    payment_methods = ['Wire Transfer', 'Check', 'Credit Card']
    payment_statuses = ['Paid', 'Pending', 'Overdue']
    
    data = []
    for i in range(n_invoices):
        po = purchase_orders.iloc[i % len(purchase_orders)]
        invoice_date = po['order_date'] + timedelta(days=random.randint(1, 30))
        due_date = invoice_date + timedelta(days=30)
        payment_date = due_date + timedelta(days=random.randint(-10, 20))
        
        invoice_amount = po['total_amount']
        tax_amount = round(invoice_amount * random.uniform(0.05, 0.15), 2)
        discount_amount = round(invoice_amount * random.uniform(0, 0.1), 2)
        final_amount = invoice_amount + tax_amount - discount_amount
        
        payment_status = 'Paid' if payment_date <= datetime.now() else random.choice(['Pending', 'Overdue'])
        late_payment = payment_date > due_date if payment_status == 'Paid' else False
        
        data.append({
            'invoice_id': f'INV-{str(i+1).zfill(4)}',
            'po_id': po['po_id'],
            'invoice_date': invoice_date,
            'payment_date': payment_date if payment_status == 'Paid' else None,
            'invoice_amount': invoice_amount,
            'amount': final_amount,
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'payment_status': payment_status,
            'payment_method': random.choice(payment_methods),
            'due_date': due_date,
            'late_payment_flag': late_payment
        })
    
    return pd.DataFrame(data)

def generate_contracts(suppliers, n_contracts):
    """Generate contract data."""
    
    contract_types = ['Service', 'Product', 'Mixed']
    compliance_statuses = ['Compliant', 'Under Review', 'Non-Compliant']
    
    data = []
    for i in range(n_contracts):
        start_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 200))
        end_date = start_date + timedelta(days=random.randint(365, 1095))  # 1-3 years
        renewal_date = end_date - timedelta(days=30)
        
        contract_value = round(random.uniform(50000, 500000), 2)
        volume_commitment = round(contract_value * random.uniform(0.8, 1.2), 2)
        
        data.append({
            'contract_id': f'CON-{str(i+1).zfill(3)}',
            'supplier_id': suppliers.iloc[i % len(suppliers)]['supplier_id'],
            'start_date': start_date,
            'end_date': end_date,
            'contract_value': contract_value,
            'volume_commitment': volume_commitment,
            'dispute_count': random.randint(0, 3),
            'compliance_status': random.choice(compliance_statuses),
            'contract_type': random.choice(contract_types),
            'renewal_date': renewal_date,
            'terms_conditions': 'Standard terms and conditions apply',
            'performance_metrics': 'Quality, Delivery, Cost',
            'penalty_clauses': 'Late delivery penalties apply'
        })
    
    return pd.DataFrame(data)

def generate_budgets(n_budgets):
    """Generate budget data."""
    
    departments = ['IT', 'HR', 'Finance', 'Operations', 'Marketing', 'Sales', 'Legal', 'Facilities']
    categories = ['Equipment', 'Services', 'Supplies', 'Software', 'Travel', 'Training']
    budget_statuses = ['Active', 'Overspent', 'Underutilized']
    fiscal_years = ['2023', '2024', '2025']
    
    data = []
    for i in range(n_budgets):
        budget_amount = round(random.uniform(50000, 500000), 2)
        allocated_amount = round(budget_amount * random.uniform(0.7, 1.0), 2)
        spent_amount = round(allocated_amount * random.uniform(0.3, 1.1), 2)
        remaining_amount = allocated_amount - spent_amount
        
        approval_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 100))
        
        data.append({
            'budget_code': f'BUD-{i+1}',
            'department': random.choice(departments),
            'category': random.choice(categories),
            'fiscal_year': random.choice(fiscal_years),
            'budget_amount': budget_amount,
            'amount': budget_amount,
            'period': 'Annual',
            'budget_id': f'BID-{i+1}',
            'allocated_amount': allocated_amount,
            'spent_amount': spent_amount,
            'remaining_amount': remaining_amount,
            'budget_status': budget_statuses[0] if spent_amount <= allocated_amount else budget_statuses[1],
            'approval_date': approval_date
        })
    
    return pd.DataFrame(data)

def generate_rfqs(suppliers, items, n_rfqs):
    """Generate RFQ data."""
    
    rfq_statuses = ['Open', 'Closed', 'Awarded', 'Cancelled']
    
    data = []
    for i in range(n_rfqs):
        issue_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 300))
        due_date = issue_date + timedelta(days=random.randint(7, 30))
        response_date = issue_date + timedelta(days=random.randint(1, 14))
        
        quantity = random.randint(10, 500)
        unit_price = round(random.uniform(20, 1500), 2)
        
        technical_score = round(random.uniform(60, 95), 1)
        commercial_score = round(random.uniform(60, 95), 1)
        evaluation_score = (technical_score + commercial_score) / 2
        
        data.append({
            'rfq_id': f'RFQ-{str(i+1).zfill(3)}',
            'supplier_id': suppliers.iloc[i % len(suppliers)]['supplier_id'],
            'item_id': items.iloc[i % len(items)]['item_id'],
            'unit_price': unit_price,
            'response_date': response_date,
            'issue_date': issue_date,
            'due_date': due_date,
            'status': random.choice(rfq_statuses),
            'quantity': quantity,
            'awarded_supplier_id': suppliers.iloc[i % len(suppliers)]['supplier_id'] if random.random() < 0.3 else None,
            'evaluation_score': evaluation_score,
            'technical_score': technical_score,
            'commercial_score': commercial_score
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    generate_sample_data() 