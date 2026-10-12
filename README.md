# Login & To-Do Application

## 1. Project Description

This project is a Login and To-Do Application developed using Python, Flask, and MySQL. Users can create an account, log in, and manage their personal tasks.

Each user can add, edit, complete, and delete tasks. Users can only see and manage their own tasks.

## 2. Technologies Used

- Python
- Flask
- MySQL
- PyMySQL
- bcrypt
- python-dotenv
- HTML and CSS

## 3. Features

- User registration and login
- Password hashing using bcrypt
- Validation for required fields
- Prevents registering with an existing email
- Add new tasks
- Edit task titles
- Mark tasks as completed or undo completion
- Delete tasks with confirmation
- Tasks are displayed newest first
- Each user has a private task list
- Responsive interface

## 4. Database Structure

The database is named `registration` and contains two tables:

- **users:** Stores user IDs, names, email addresses, password hashes, and registration dates.
- **todos:** Stores task IDs, the associated user ID, task titles, completion status, and creation dates.

The database structure is provided in `database/schema.sql`.

## 5. Installation and Running

### Requirements

Install Python and MySQL first.

### Install the required packages

Open a terminal in the project folder and run:

```bash
python -m pip install flask pymysql bcrypt python-dotenv
```

### Configure environment variables

Create a `.env` file in the project folder using `.env.example` as a guide.

Enter your own MySQL username and password and a random secret key. Do not upload `.env` to GitHub.

### Set up the database

Run the SQL commands in `database/schema.sql` using MySQL Workbench or DBeaver.

### Run the application

Open a terminal in the project folder and run:

```bash
python app.py
```

Open this address in your browser:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

## 6. Team Members and Contributions

Replace the information below with the actual names, student IDs, and contributions of your group members.

- **Member 1:** [Amir Ehab Madih] — [2304022]&#x20;
- **Member 2: [Hussin Mohamed Elnakib**] — [2304272]&#x20;

## 7. Assignment Questions

### A. Why do UPDATE and DELETE statements include `AND user_id = ?`? What happens if it is removed?

It makes sure that a user can only update or delete their own tasks. If it is removed, a user might change or delete another user's task by using its task ID.

### B. What happens if a task is inserted with a user ID that does not exist? Which database constraint prevents it?

The database rejects the insert because the user ID must refer to an existing user. The foreign key constraint prevents it.

### C. Why store a password hash instead of the original password?

A password hash protects the original password from being stored directly in the database. If the database is exposed, the original passwords are not immediately visible.

### D. If the name column is NOT NULL, why check whether the name is empty?

NOT NULL prevents a value of NULL, but it does not prevent an empty string or a string containing only spaces. The application checks the name to make sure the user enters an actual name.
