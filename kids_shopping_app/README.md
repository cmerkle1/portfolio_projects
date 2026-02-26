### 🗞️ [News App](./news_application)
A full-stack news app built with Django, MySQL, and Docker. Allows the user to register as a journalist, reader, or editor. Journalists can create, edit, and delete articles and newsletters. Editors can edit, approve, or delete articles written by journalists. Once approved, journalist articles appear on the main page and can be subscribed to by readers. If a reader is subscribed to a journalist, they will receive an email when their journalist publishes a newsletter.

<br>
<details>
<summary><strong>📸 Click here to view App Screenshots</strong></summary>
<br>
<img src="./news_application/static/main.png" alt="Main Page" width="600">
<br><br>
<img src="./news_application/static/signup.png" alt="Sign-up Form" width="600">
<br><br>
<img src="./news_application/static/articleview.png" alt="Article View" width="600">
</details>
<br>

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
