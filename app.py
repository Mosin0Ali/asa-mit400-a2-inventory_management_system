from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pymysql
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# -------------------------------
# 🧩 Database Connection Helper
# -------------------------------
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='worxpro@1234',  # your password
        database='inventory_db',
        cursorclass=pymysql.cursors.DictCursor
    )

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def dashboard():
    conn = get_connection()
    with conn.cursor() as cur:
        # --- Weekly Sales (Last 7 Days) ---
        cur.execute("""
            SELECT 
                DATE_FORMAT(sale_date, '%a') AS day,
                SUM(total_amount) AS total
            FROM sales
            WHERE sale_date >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE_FORMAT(sale_date, '%a'), DAYOFWEEK(sale_date)
            ORDER BY DAYOFWEEK(sale_date);
        """)
        sales_rows = cur.fetchall()

        # Map results to ensure all 7 days show, even if 0
        days_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        sales_map = {row['day']: float(row['total']) for row in sales_rows}
        sales_data = {
            'labels': days_order,
            'values': [sales_map.get(day, 0) for day in days_order]
        }
        
        # --- Top Products by Stock Levels ---
        cur.execute("""
            SELECT 
                name AS product_name,
                stock_quantity AS stock_level
            FROM products
            ORDER BY stock_quantity ASC
            LIMIT 5;
        """)
        top_rows = cur.fetchall()
        top_products = {
            'labels': [r['product_name'] for r in top_rows],
            'values': [r['stock_level'] for r in top_rows]
        }

    conn.close()
    
    return render_template('dashboard.html', sales_data=sales_data, top_products=top_products)

# -------------------------------
# 🧱 PRODUCTS
# -------------------------------


@app.route('/sales_report')
def sales_report():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                p.name AS product_name,
                SUM(si.quantity_sold) AS total_sales,
                SUM(si.quantity_sold * si.sale_price ) AS total_revenue,
                SUM(si.quantity_sold * p.cost_price) AS cost_price_p
                
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date >= CURDATE() - INTERVAL 30 DAY
            GROUP BY p.product_id, p.name
            ORDER BY total_revenue DESC
            LIMIT 5;
        """)
        top_rows = cur.fetchall()
        sales_report = top_rows
        top_products = {
            'labels': [r['product_name'] for r in top_rows],
            'values': [float(r['total_sales']) for r in top_rows]
        }
    conn.close()
    return render_template('salesreport.html', sales_report=sales_report,top_products=top_products)



@app.route('/products')
def products():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['description'],
            int(request.form['stock_quantity']),
            float(request.form['unit_price']),
            float(request.form['cost_price']),
            int(request.form['reorder_point']),
            datetime.now()
        )
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO products (name, description, stock_quantity, unit_price, cost_price, reorder_point, date_added)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)
        conn.commit()
        conn.close()
        flash('✅ Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM products WHERE product_id=%s", (id,))
        product = cur.fetchone()

        if request.method == 'POST':
            updated_data = (
                request.form['name'],
                request.form['description'],
                int(request.form['stock_quantity']),
                float(request.form['unit_price']),
                float(request.form['cost_price']),
                int(request.form['reorder_point']),
                id
            )
            cur.execute("""
                UPDATE products SET name=%s, description=%s, stock_quantity=%s,
                unit_price=%s, cost_price=%s, reorder_point=%s WHERE product_id=%s
            """, updated_data)
            conn.commit()
            flash('✏️ Product updated successfully!', 'info')
            return redirect(url_for('products'))
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:id>')
def delete_product(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM sale_items WHERE product_id=%s", (id,))
        cur.execute("DELETE FROM products WHERE product_id=%s", (id,))
    conn.commit()
    conn.close()
    flash('🗑️ Product deleted successfully!', 'danger')
    return redirect(url_for('products'))

# -------------------------------
# 🛒 CREATE ORDER
# -------------------------------

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        total_amount = 0
        sale_items = []

        conn = get_connection()
        with conn.cursor() as cur:
            for pid, qty in zip(product_ids, quantities):
                qty = int(qty)
                if qty <= 0:
                    continue

                cur.execute("SELECT * FROM products WHERE product_id=%s", (pid,))
                product = cur.fetchone()
                if not product:
                    continue

                if product['stock_quantity'] < qty:
                    flash(f"Not enough stock for {product['name']}! Available: {product['stock_quantity']}", 'danger')
                    return redirect(url_for('create_order'))

                total_amount += float(product['unit_price']) * qty
                sale_items.append((pid, qty, float(product['unit_price'])))

            if not sale_items:
                flash("⚠️ No products selected!", "warning")
                return redirect(url_for('create_order'))

            # Insert sale
            cur.execute("""
                INSERT INTO sales (sale_date, customer_name, total_amount)
                VALUES (%s, %s, %s)
            """, (datetime.now(), customer_name, total_amount))
            sale_id = cur.lastrowid

            # Insert sale items + update stock
            for pid, qty, price in sale_items:
                cur.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity_sold, sale_price)
                    VALUES (%s, %s, %s, %s)
                """, (sale_id, pid, qty, price))
                cur.execute("""
                    UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id=%s
                """, (qty, pid))

        conn.commit()
        conn.close()
        flash('✅ Order created successfully!', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('create_order.html', products=products)

# -------------------------------
# 🔁 RETURN ORDER
# -------------------------------

@app.route('/return_order', methods=['GET', 'POST'])
def return_order():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM sales ORDER BY sale_date DESC")
        sales = cur.fetchall()

    if request.method == 'POST':
        sale_id = int(request.form.get('sale_id'))
        product_id = int(request.form.get('product_id'))
        qty_to_return = int(request.form.get('quantity'))

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sale_items WHERE sale_id=%s AND product_id=%s", (sale_id, product_id))
            sale_item = cur.fetchone()

            cur.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
            product = cur.fetchone()

            if not sale_item or not product:
                flash("Invalid sale or product selected.", "danger")
                return redirect(url_for('return_order'))

            if qty_to_return > sale_item['quantity_sold']:
                flash("Return quantity cannot exceed sold quantity.", "danger")
                return redirect(url_for('return_order'))

            # Update stock
            cur.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id=%s", (qty_to_return, product_id))

            # Adjust sale item
            remaining_qty = sale_item['quantity_sold'] - qty_to_return

            if remaining_qty > 0:
                cur.execute("""
                    UPDATE sale_items
                    SET quantity_sold=%s
                    WHERE sale_id=%s AND product_id=%s
                """, (remaining_qty, sale_id, product_id))
            else:
                cur.execute("DELETE FROM sale_items WHERE sale_id=%s AND product_id=%s", (sale_id, product_id))

            # Recalculate sale total
            cur.execute("SELECT SUM(quantity_sold * sale_price) AS total FROM sale_items WHERE sale_id=%s", (sale_id,))
            total = cur.fetchone()['total']

            if total is None:
                cur.execute("DELETE FROM sales WHERE sale_id=%s", (sale_id,))
            else:
                cur.execute("UPDATE sales SET total_amount=%s WHERE sale_id=%s", (total, sale_id))

        conn.commit()
        conn.close()
        flash("Return processed successfully.", "success")
        return redirect(url_for('return_order'))

    conn.close()
    return render_template('return_order.html', sales=sales)

# -------------------------------
# 🔍 API - Sale Items by Sale ID
# -------------------------------

@app.route('/api/sale-items/<int:sale_id>')
def get_sale_items(sale_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT si.product_id, p.name AS product_name, si.quantity_sold, si.sale_price
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            WHERE si.sale_id=%s
        """, (sale_id,))
        items = cur.fetchall()
    conn.close()
    return jsonify({'items': items})

# -------------------------------
# 🚀 RUN
# -------------------------------

if __name__ == '__main__':
    app.run(debug=True)
