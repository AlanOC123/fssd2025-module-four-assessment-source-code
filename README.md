# Projectify: Organize Your Thoughts into Actions

Projectify is a modern, single-user productivity application designed to help you organize your life. Built with Flask and PostgreSQL, it allows you to segment your goals and tasks into distinct **Identities** (like "The Learner" or "The Builder") and manage your **Projects**, **Tasks**, and **Thoughts** within those contexts.

The application features a fully responsive UI, a dynamic and database-driven theme system, and a robust API for a fast, modern user experience.

## ✨ Features

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

## 🛠️ Tech Stack & Architecture

### Backend

* **Framework:** Flask
* **Database:** PostgreSQL
* **ORM:** Flask-SQLAlchemy
* **Migrations:** Flask-Migrate
* **Authentication:** Flask-Login, Flask-WTF (for CSRF), bcrypt
* **Server:** Gunicorn

### Frontend

* **Templating:** Jinja2
* **Styling:** A custom, modern CSS system built with CSS variables, HSL-based colors, `clamp()` for fluid typography, and grid/flexbox for responsive layouts.
* **JavaScript:** Vanilla JavaScript (ES6 Modules) using `async/await` and the `fetch` API for all asynchronous actions (deleting/editing thoughts, tasks, etc.).

### 🏛️ Architecture

This project is built using a highly organized, professional-grade structure:

* **Application Factory Pattern:** The app is created using a `create_app` factory (`app/__init__.py`).
* **Blueprints:** The app is modularized into `app`, `auth`, `settings`, `api`, and `info` blueprints.
* **Manager Class Architecture:** All database logic is abstracted into a robust manager pattern. A central `DatabaseManager` holds instances of `ProfileManager`, `ProjectManager`, `TaskManager`, etc. This keeps the routes clean and all business logic centralized.
* **Atomic Transactions:** All database operations that affect multiple tables (e.g., creating a task and updating its project) are wrapped in a single `try/except/rollback` block to ensure data integrity.
* **Database Seeding:** The project includes custom CLI commands (`flask reset-db`, `flask seed-db`) to initialize the database with data from JSON files.

## ⚙️ Local Installation

### 1. Prerequisites

* Python 3.10+
* PostgreSQL running locally or on a server.

### 2. Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/AlanOC123/fssd2025-module-four-assessment-source-code.git](https://github.com/AlanOC123/fssd2025-module-four-assessment-source-code.git)
    cd fssd2025-module-four-assessment-source-code
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up a Postgres Database:**
    Before you can create your `.env` file, you need to create the database that your app will connect to.
    Make sure PostgreSQL is installed and running on your system.
    Open your command-line terminal and start the PostgreSQL interactive shell:
    ```bash
    psql -U postgres
    ```
    (You may need to enter the password you created when you installed Postgres).

    Inside the `psql` shell, run the following commands:
    ```sql
    -- 1. Create a password for this project (use a secure password)
    CREATE USER projectify_user WITH PASSWORD 'your_secure_password_here';

    -- 2. Create the database for testing
    CREATE DATABASE projectify_dev;

    -- 3. Give your new user permission to control this new database
    GRANT ALL PRIVILEGES ON DATABASE projectify_dev TO projectify_user;

    -- 4. Exit the psql shell
    \q
    ```

5.  **Create your .env file:**
    Create a file named `.env` in the root of the project. This file stores your secret keys.
    ```dotenv
    # Generate a strong, random string (e.g using python secrets library)
    SECRET_KEY='your_super_secret_key'

    # Set this to 'testing' to use the test config
    FLASK_CONFIG='testing'

    # Your PostgreSQL connection string
    # Use the values you just created in step 4.
    # format: postgresql://[user]:[password]@[host]:[port]/[database_name]
    DATABASE_URL_TEST='postgresql://projectify_user:your_secure_password_here@localhost:5432/projectify_dev'

    # This is for your live website (e.g., on Render)
    DATABASE_URL_PROD='your_production_db_url'
    ```

### 3. Running the Application

1.  **Initialize the Database:**
    This command will delete all existing data, create all tables, and seed the database with default themes, identities, and a test user.
    ```bash
    flask reset-db
    ```
    * **Test User:** Created by the seed command.
    * **Email:** `testuser@projectify.com`
    * **Password:** `Test!12345`

2.  **Run the app:**
    ```bash
    flask run
    ```
    The application will be running at `http://127.0.0.1:8080`.

## 🚀 Deployment

This application is configured for deployment on **Render.com**.

### Instructions for Deploying on Render:

1.  **GitHub:** Ensure your project is pushed to a GitHub repository.
2.  **Create PostgreSQL Database:**
    * On Render, create a new "PostgreSQL" service.
    * Fill out a name and region.
    * Once created, copy the **Internal Connection String**.
3.  **Create Web Service:**
    * On Render, create a new "Web Service" and connect it to your GitHub repository.
    * In the settings, set the **Build Command** to: `pip install -r requirements.txt`
    * Set the **Start Command** to: `gunicorn 'app:create_app("production")'`
4.  **Add Environment Variables:**
    * Go to your Web Service's "Environment" tab.
    * Add `SECRET_KEY` and set it to a new, secure random string.
    * Add `FLASK_CONFIG` and set its value to `production`.
    * Add `DATABASE_URL_PROD` and paste the **Internal Connection String** you copied from your Render database.
5.  **Run Migrations & Seed:**
    * After the first build, go to your Web Service's "Shell" tab.
    * Run `flask db upgrade` to apply your database migrations.
    * Run `flask seed-db` to add the default themes and identity templates.
6.  **Deploy:**
    * Trigger a manual deploy. Your application will be live at the URL provided by Render.

### ⚠️ Deployment Migration Error?

If your first deployment fails on `flask db upgrade` with an `UndefinedTable` error, it means your local migration history is out of sync. **Do not delete the folder on the server.**

To fix this **locally**:
1.  Delete the `migrations/` folder in your local project.
2.  Drop all tables in your *local* database (e.g., using `psql` or `flask reset-db`).
3.  Run `flask db init` to recreate the `migrations/` folder.
4.  Run `flask db migrate -m "Initial database models"` to create a single, correct migration file that includes all `create_table` commands.
5.  Commit and push the new `migrations/` folder to GitHub.
6.  Manually trigger a new deploy on Render. The `flask db upgrade` command will now work.
