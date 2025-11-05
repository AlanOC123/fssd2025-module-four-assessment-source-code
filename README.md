# **Projectify: Organize Your Thoughts into Actions**

Projectify is a modern, single-user productivity application designed to help you organize your life. Built with Flask and PostgreSQL, it allows you to segment your goals and tasks into distinct **Identities** (like "The Learner" or "The Builder") and manage your **Projects**, **Tasks**, and **Thoughts** within those contexts.

The application features a fully responsive UI, a dynamic and database-driven theme system, and a robust API for a fast, modern user experience.

## **✨ Features**

* **Full Authentication:** Secure user registration and login system using Flask-Login and bcrypt password hashing.  
* **The "Identities" Concept:** The core of the app. Users have multiple "Identities" (e.g., "Learner," "Creator," "Health Nut") which act as high-level filters for all projects, tasks, and thoughts.  
* **Project Management:** Full CRUD (Create, Read, Update, Delete) for projects. Projects have names, descriptions, start/end dates, and a status that is *automatically* calculated based on the tasks within it.  
* **Task Management:** Full, asynchronous CRUD for tasks, which belong to projects. Tasks have due dates, difficulty levels, and a "complete" status.  
* **Atomic Operations:** Creating, editing, or deleting a task automatically updates the parent project's status (e.g., "In Progress," "Completed") in a single, safe database transaction.  
* **Thoughts Journal:** A "chat-style" journal for each identity, complete with a filterable timeline, date/hour grouping, and full async CRUD.  
* **Advanced Settings Panel:** A comprehensive, multi-page settings area where users can:  
  * Update personal info.  
  * Change their email or password (with secure current password verification).  
  * Customize their identity names.  
  * Delete their account securely.  
* **Dynamic Theme Engine:** A powerful, database-driven theme system.  
  * **Color Scheme:** Users can select from multiple color schemes (e.g., "Ocean Blue," "Forest Green") which dynamically injects CSS variables (HSL hues) into the root.  
  * **Theme Mode:** Users can toggle between Light, Dark, and System modes.

## **🛠️ Tech Stack & Architecture**

### **Backend**

* **Framework:** Flask  
* **Database:** PostgreSQL  
* **ORM:** Flask-SQLAlchemy  
* **Migrations:** Flask-Migrate (with manually edited migrations for native PGSQL enums)  
* **Authentication:** Flask-Login, Flask-WTF (for CSRF), bcrypt  
* **Server:** Gunicorn

### **Frontend**

* **Templating:** Jinja2  
* **Styling:** A custom, modern CSS system built with CSS variables, HSL-based colors, clamp() for fluid typography, and grid/flexbox for responsive layouts.  
* **JavaScript:** Vanilla JavaScript (ES6 Modules) using async/await and the fetch API for all asynchronous actions (deleting/editing thoughts, tasks, etc.).

### **🏛️ Architecture**

This project is built using a highly organized, professional-grade structure:

* **Application Factory Pattern:** The app is created using a create\_app factory (app/\_\_init\_\_.py).  
* **Blueprints:** The app is modularized into app, auth, settings, api, and info blueprints.  
* **Manager Class Architecture:** All database logic is abstracted into a robust manager pattern. A central DatabaseManager holds instances of ProfileManager, ProjectManager, TaskManager, etc. This keeps the routes clean and all business logic centralized.  
* **Atomic Transactions:** All database operations that affect multiple tables (e.g., creating a task and updating its project) are wrapped in a single try/except/rollback block with session.flush() and session.commit() to ensure data integrity.  
* **Database Seeding:** The project includes custom CLI commands (flask reset-db, flask seed-db) to initialize the database with data from JSON files.

## **⚙️ Local Installation**

### **1\. Prerequisites**

* Python 3.10+  
* PostgreSQL running locally or on a server.

### **2\. Setup**

1. **Clone the repository:**  
   git clone \[https://github.com/your-username/your-repo-name.git\](https://github.com/your-username/your-repo-name.git)  
   cd your-repo-name

2. **Create and activate a virtual environment:**  
   python3 \-m venv .venv  
   source .venv/bin/activate

3. **Install dependencies:**  
   pip install \-r requirements.txt

4. Create your .env file:  
   Create a file named .env in the root of the project. This file stores your secret keys.  
   \# Generate a strong, random string (e.g., using \`python \-c 'import secrets; print(secrets.token\_hex(24))'\`)  
   SECRET\_KEY='your\_super\_secret\_key'

   \# Set this to 'testing' to use the test config  
   FLASK\_CONFIG='testing'

   \# Your PostgreSQL connection string  
   \# format: postgresql://\[user\]:\[password\]@\[host\]:\[port\]/\[database\_name\]  
   DATABASE\_URL\_TEST='postgresql://user:password@localhost:5432/projectify\_dev'  
   DATABASE\_URL\_PROD='your\_production\_db\_url'

### **3\. Running the Application**

1. Initialize the Database:  
   This command will delete all existing data, create all tables, and seed the database with default themes, identities, and a test user.  
   flask reset-db

   * **Test User:** Created by the seed command.  
   * **Email:** testuser@projectify.com  
   * **Password:** Test\!12345  
2. **Run the app:**  
   flask run

   The application will be running at http://127.0.0.1:8080.

## **🚀 Deployment**

This application is configured for deployment on **Render.com**.

### **Instructions for Deploying on Render:**

1. **GitHub:** Ensure your project is pushed to a GitHub repository.  
2. **Create PostgreSQL Database:**  
   * On Render, create a new "PostgreSQL" service.  
   * Fill out a name and region.  
   * Once created, copy the **Internal Connection String**.  
3. **Create Web Service:**  
   * On Render, create a new "Web Service" and connect it to your GitHub repository.  
   * In the settings, set the **Build Command** to: pip install \-r requirements.txt  
   * Set the **Start Command** to: gunicorn 'app:create\_app(\\"production\\")'  
4. **Add Environment Variables:**  
   * Go to your Web Service's "Environment" tab.  
   * Add a SECRET\_KEY and set it to a new, secure random string.  
   * Add FLASK\_CONFIG and set its value to production.  
   * Add DATABASE\_URL\_PROD and paste the **Internal Connection String** you copied from your Render database.  
5. **Run Migrations & Seed:**  
   * After the first build, go to your Web Service's "Shell" tab.  
   * Run flask db upgrade to apply your database migrations.  
   * Run flask seed-db to add the themes, identities, and test user.  
6. **Deploy:**  
   * Trigger a manual deploy. Your application will be live at the URL provided by Render.