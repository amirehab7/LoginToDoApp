
from flask import Flask, render_template, request, redirect, session
import pymysql
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "registration"),
        port=int(os.getenv("DB_PORT", "3306")),
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            error = "Name is required"
        elif not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        elif not confirm_password:
            error = "Confirm password is required"
        elif password != confirm_password:
            error = "Passwords do not match"
        elif len(password) < 8:
            error = "Password must be at least 8 characters"

        if error:
            return render_template("register.html", error=error), 400

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (name, email, password_hash)
                )
                user_id = cursor.lastrowid

            connection.commit()

            session["user_id"] = user_id
            session["user_name"] = name

            return redirect("/todos")

        except pymysql.err.IntegrityError:
            connection.rollback()
            return render_template(
                "register.html",
                error="Email Already Exists"
            ), 400

        finally:
            connection.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"
        else:
            connection = get_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT user_id, name, password_hash "
                        "FROM users WHERE email = %s",
                        (email,)
                    )
                    user = cursor.fetchone()

                if user and bcrypt.checkpw(
                    password.encode("utf-8"),
                    user["password_hash"].encode("utf-8")
                ):
                    session.clear()
                    session["user_id"] = user["user_id"]
                    session["user_name"] = user["name"]
                    return redirect("/todos")

                error = "Invalid email or password"

            finally:
                connection.close()

        return render_template("login.html", error=error), 400

    return render_template("login.html", error=error)


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT todo_id, title, is_done FROM todos "
                "WHERE user_id = %s ORDER BY created_at DESC",
                (session["user_id"],)
            )
            user_todos = cursor.fetchall()
    finally:
        connection.close()

    return render_template(
        "todos.html",
        todos=user_todos,
        name=session["user_name"]
    )


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title", "").strip()

    if not title:
        return "Title is required", 400

    if len(title) > 200:
        return "Title is too long", 400

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                (session["user_id"], title)
            )
        connection.commit()
    finally:
        connection.close()

    return redirect("/todos")


@app.route("/todos/edit/<int:todo_id>", methods=["GET", "POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT todo_id, title FROM todos "
                "WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"])
            )
            todo = cursor.fetchone()

            if not todo:
                return "Task not found", 404

            error = None

            if request.method == "POST":
                title = request.form.get("title", "").strip()

                if not title:
                    error = "Title is required"
                elif len(title) > 200:
                    error = "Title is too long"
                else:
                    cursor.execute(
                        "UPDATE todos SET title = %s "
                        "WHERE todo_id = %s AND user_id = %s",
                        (title, todo_id, session["user_id"])
                    )
                    connection.commit()
                    return redirect("/todos")

            return render_template(
                "edit_todo.html",
                todo=todo,
                error=error
            )
    finally:
        connection.close()

@app.route("/todos/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET is_done = NOT is_done "
                "WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"])
            )
        connection.commit()
    finally:
        connection.close()

    return redirect("/todos")


@app.route("/todos/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"])
            )
        connection.commit()
    finally:
        connection.close()

    return redirect("/todos")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
