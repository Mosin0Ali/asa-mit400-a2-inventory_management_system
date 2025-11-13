from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# -------------------------------
# 🔗 MySQL Connection
# Update this with your credentials
# -------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:worxpro%401234@localhost/inventory_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------
# MODELS (mirror your MySQL tables)
# -------------------------------
class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    reorder_point = db.Column(db.Integer, nullable=False, default=10)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_name = db.Column(db.String(255))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    item_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.sale_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date, nullable=False)
    supplier_name = db.Column(db.String(255), nullable=False)
    expected_delivery_date = db.Column(db.Date)
    status = db.Column(db.Enum('Pending', 'Shipped', 'Received', 'Cancelled'), default='Pending')
    total_cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def dashboard():
    # Example static chart data — replace later with live sales aggregation
    sales_data = {
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'values': [150, 200, 180, 220, 170, 300, 250]
    }
  
    return render_template('dashboard.html', sales_data=sales_data)

@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        new_product = Product(
            name=request.form['name'],
            description=request.form['description'],
            stock_quantity=request.form['stock_quantity'],
            unit_price=request.form['unit_price'],
            cost_price=request.form['cost_price'],
            reorder_point=request.form['reorder_point']
        )
        db.session.add(new_product)
        db.session.commit()
        flash('✅ Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.stock_quantity = request.form['stock_quantity']
        product.unit_price = request.form['unit_price']
        product.cost_price = request.form['cost_price']
        product.reorder_point = request.form['reorder_point']
        db.session.commit()
        flash('✏️ Product updated successfully!', 'info')
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('🗑️ Product deleted successfully!', 'danger')
    return redirect(url_for('products'))

from flask import request, flash

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    products = Product.query.all()

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        total_amount = 0
        sale_items = []

        # Check inventory and only include products with qty > 0
        for pid, qty in zip(product_ids, quantities):
            product = Product.query.get(int(pid))
            qty = int(qty)

            if qty <= 0:
                continue  # Skip products that the customer does not buy

            if product.stock_quantity < qty:
                flash(f'Not enough stock for {product.name}! Available: {product.stock_quantity}', 'danger')
                return redirect(url_for('create_order'))

            total_amount += float(product.unit_price) * qty
            sale_items.append((product, qty, float(product.unit_price)))

        if not sale_items:
            flash('⚠️ No products selected!', 'warning')
            return redirect(url_for('create_order'))

        # Create sale
        sale = Sale(customer_name=customer_name, total_amount=total_amount)
        db.session.add(sale)
        db.session.flush()  # get sale_id before commit

        # Add sale items and reduce inventory
        for product, qty, price in sale_items:
            item = SaleItem(sale_id=sale.sale_id, product_id=product.product_id,
                            quantity_sold=qty, sale_price=price)
            product.stock_quantity -= qty
            db.session.add(item)

        db.session.commit()
        flash('✅ Order created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_order.html', products=products)



@app.route('/return_order', methods=['GET', 'POST'])
def return_order():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()

    if request.method == 'POST':
        sale_id = request.form.get('sale_id')
        product_id = request.form.get('product_id')
        qty_to_return = int(request.form.get('quantity'))

        sale_item = SaleItem.query.filter_by(sale_id=sale_id, product_id=product_id).first()
        product = Product.query.get(product_id)

        if not sale_item or not product:
            flash("Invalid sale or product selected.", "danger")
            return redirect(url_for('return_order'))

        if qty_to_return > sale_item.quantity_sold:
            flash("Return quantity cannot exceed sold quantity.", "danger")
            return redirect(url_for('return_order'))

        # Step 1: Update product stock
        product.stock_quantity += qty_to_return

        # Step 2: Adjust or remove sale item
        sale_item.quantity_sold -= qty_to_return
        sale_item.sale_price = (sale_item.sale_price / (sale_item.quantity_sold + qty_to_return)) * sale_item.quantity_sold \
            if sale_item.quantity_sold > 0 else 0

        if sale_item.quantity_sold <= 0:
            db.session.delete(sale_item)

        # Step 3: Recalculate total sale amount
        remaining_items = SaleItem.query.filter_by(sale_id=sale_id).all()
        if not remaining_items:
            # All items returned — delete sale
            sale = Sale.query.get(sale_id)
            db.session.delete(sale)
        else:
            sale = Sale.query.get(sale_id)
            sale.total_amount = sum(float(item.sale_price) for item in remaining_items)

        db.session.commit()
        flash("Return processed successfully.", "success")
        return redirect(url_for('return_order'))

    return render_template('return_order.html', sales=sales)

@app.route('/api/sale-items/<int:sale_id>')
def get_sale_items(sale_id):
    sale_items = SaleItem.query.filter_by(sale_id=sale_id).all()
    items_data = []
    for item in sale_items:
        product = Product.query.get(item.product_id)
        items_data.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'quantity_sold': item.quantity_sold,
            'sale_price': str(item.sale_price)
        })
    return jsonify({'items': items_data})



if __name__ == '__main__':
    app.run(debug=True)
