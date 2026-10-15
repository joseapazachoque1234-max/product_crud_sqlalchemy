from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-esta-clave-en-produccion"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///productos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products)


@app.route("/products/create", methods=["POST"])
def create_product():
    name = request.form.get("name", "").strip()
    price_text = request.form.get("price", "").strip()
    stock_text = request.form.get("stock", "0").strip() or "0"

    try:
        price = float(price_text)
        stock = int(stock_text)
        if not name:
            raise ValueError("El nombre es obligatorio.")
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
    except ValueError as error:
        flash(str(error) or "Revisa los datos ingresados.", "error")
        return redirect(url_for("index"))

    product = Product(name=name, price=price, stock=stock)
    db.session.add(product)
    db.session.commit()
    flash("Producto registrado correctamente.", "success")
    return redirect(url_for("index"))


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            price = float(request.form.get("price", "").strip())
            stock = int(request.form.get("stock", "0").strip() or "0")
            if not name:
                raise ValueError("El nombre es obligatorio.")
            if price < 0 or stock < 0:
                raise ValueError("Precio y stock deben ser valores no negativos.")
        except ValueError as error:
            flash(str(error) or "Revisa los datos ingresados.", "error")
            return render_template("edit.html", product=product)

        product.name = name
        product.price = price
        product.stock = stock
        db.session.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", product=product)


@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
