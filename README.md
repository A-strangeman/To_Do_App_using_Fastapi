# 📝 To Do App using FastAPI

A simple and clean To-Do List web application built using FastAPI and SQLAlchemy.

This project demonstrates CRUD operations, database integration, and basic full-stack structure using templates and static files.

---

## 🚀 Features

- ✅ Create new tasks
- 📋 View all tasks
- ✏️ Update tasks
- ❌ Delete tasks
- 🗄️ Database integration using SQLAlchemy
- 🌐 Template rendering using Jinja2
- ⚡ FastAPI backend

---

## 🛠️ Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite
- Jinja2 Templates
- HTML & CSS

---

## 📂 Project Structure


To_Do_App_using_Fastapi
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── routers/
├── templates/
├── static/
├── .env
├── .gitignore
└── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository


git clone https://github.com/A-strangeman/To_Do_App_using_Fastapi.git

cd To_Do_App_using_Fastapi


### 2️⃣ Create virtual environment


python -m venv venv
venv\Scripts\activate


### 3️⃣ Install dependencies


pip install -r requirements.txt


### 4️⃣ Create `.env` file

Create a `.env` file in the root folder:


DATABASE_URL=postgresql://username:password@localhost:5432/todo_db


(Or use SQLite if configured)

### 5️⃣ Run the server


uvicorn main:app --reload


Open in browser:


http://127.0.0.1:8000


---

## 📖 API Documentation

FastAPI automatically generates docs:


http://127.0.0.1:8000/docs


---

## 📌 Future Improvements

- 🔐 User Authentication
- 🌍 Deploy to cloud (Render / Railway)
- 🎨 Improve UI design
- 📊 Add task status filtering

---

## 👨‍💻 Author

Roshan Gupta  
B.Tech Computer Science Student  
Learning Backend Development 🚀

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!