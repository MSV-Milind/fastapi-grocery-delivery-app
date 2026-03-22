# FreshMart Grocery API

This project was built as part of the FastAPI Internship final project. The objective was to build a grocery management API step-by-step using concepts taught from Day 1 to Day 6 such as routing, validation, CRUD operations, workflows, and search features.

The project simulates a simple grocery store backend where users can view items, place orders, manage a cart, and perform searches.

## What was implemented

- Basic GET routes for items and orders.
- Pydantic validation for order requests.
- Helper functions for item lookup and order calculations.
- POST endpoint for placing orders.
- Bulk order discount logic.
- Filtering items by category, price, unit and stock status.
- CRUD operations for grocery items.
- Cart workflow (add, view, remove, checkout).
- Search functionality across item name and category.
- Sorting and pagination for items and orders.
- Combined browse endpoint with filters, sorting & pagination.

## How to run the project locally
In terminal, do the following:

1) Clone the repository:
```
git clone https://github.com/MSV-Milind/fastapi-grocery-delivery-app.git
```

2) Go into the project folder
```
cd fastapi-grocery-delivery-api
```

3) Create virtual environment:
```
python3 -m venv venv
```

4) Activate Virtual Environment
Mac/Linux:
```
source venv/bin/activate
```
Windows:
```
venv\Scripts\activate
```

5) Install Dependencies
```
pip install -r requirements.txt
```

6) Run the server 
```
uvicorn main:app --reload
```

7) Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

All endpoints can be tested from there.

## Conclusion

This project helped me understand how different API components connect together, especially multi-step workflows like cart checkout and combined filtering/search logic. It also gave good practice in structuring backend code properly instead of just writing isolated endpoints.
