### 🧸 [Ecommerce App](./kids_shopping_app)
A full-stack e-commerce app built with Django, MySQL, and Docker. Allows the user to register as either a buyer or a seller. A buyer may browse the marketplace and sort by price or by seller, add items to a cart and edit or remove them, place an order and receive an email confirmation, and leave reviews. The buyer can leave a verified review if they have purchased the item, or an unverified review if they have not. Sellers have the ability to list items for sale by adding a photo, title, description, price, and available/unavailable status.

<br>
<details>
<summary><strong>📸 Click here to view App Screenshots</strong></summary>
<br>
<h4>Store View</h4>
<img src="./kids_shopping_app/staticfiles/shopping_app/storefront.png" alt="Store View" width="600">
<br><br>
<h4>Login Form</h4>
<img src="./kids_shopping_app/staticfiles/shopping_app/login.png" alt="Login Form" width="600">
<br><br>
<h4>Register Form</h4>
<img src="./kids_shopping_app/staticfiles/shopping_app/create.png" alt="Create Form" width="600">
<br><br>
<h4>Item Details</h4>
<img src="./kids_shopping_app/staticfiles/shopping_app/itemview.png" alt="Item Details Page" width="600">
</details>

#### Instructions
This project is containerized using Docker. You do not need to install Python or MySQL locally to run it. Clone the repository and follow the steps below:

1. **Navigate to the project folder:**
   ```bash
   cd kids_shopping_app

2. **Build and Start the App:**
   ```bash
   docker compose up --build

3. **Set up the Database (New Terminal):**
   ```bash
   docker compose exec web python manage.py migrate

4. **View the App:**
   Navigate to http://localhost:8000
