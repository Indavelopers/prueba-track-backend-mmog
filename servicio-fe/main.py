from flask import Flask, render_template
from google.cloud import firestore


app = Flask(__name__)

db = firestore.Client() # Using '(default)' Cloud Firestore DB

@app.route("/catalogue")
def get_catalogue():
    """
    Lists every document in the 'productos' collection from Cloud Firestore
    and renders them in an HTML template.
    """
    try:
        products_ref = db.collection("productos")
        docs = products_ref.stream()

        products = []
        for doc in docs:
            product_data = doc.to_dict()
            products.append(product_data)

        return render_template("catalogue.html", products=products)

    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
