from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# --------------DATASET--------------------
items = [
    {"id":1,"name":"Basmati Rice","price":125,"unit":"kg","category":"Grain","in_stock":True},
    {"id":2,"name":"Heritage Milk","price":74,"unit":"litre","category":"Dairy","in_stock":True},
    {"id":3,"name":"Amul Paneer","price":410,"unit":"kg","category":"Dairy","in_stock":False},
    {"id":4,"name":"Kiwi","price":199,"unit":"kg","category":"Fruit","in_stock":True},
    {"id":5,"name":"Curd","price":55,"unit":"litre","category":"Dairy","in_stock":True},
    {"id":6,"name":"Carrot","price":40,"unit":"kg","category":"Vegetable","in_stock":False},
]

orders=[]
order_counter=1
cart=[]

# ---------Pydantic Models---------------
#Q6 Order Request
class OrderRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    item_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=50)
    delivery_address:str=Field(...,min_length=10)
    delivery_slot:str="Morning"
    bulk_order:bool=False

class CheckoutRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    delivery_address:str=Field(...,min_length=10)
    delivery_slot:str="Morning"

class NewItem(BaseModel):
    name:str=Field(...,min_length=2)
    price:int=Field(...,gt=0)
    unit:str=Field(...,min_length=2)
    category:str=Field(...,min_length=2)
    in_stock:bool=True

# -----------Helper Functions--------------
def find_item(item_id:int):
    for item in items:
        if item["id"]==item_id:
            return item
    return None

def calculate_total(price,quantity,delivery_slot,bulk_order=False):
    original_total=price*quantity
    discount=0
    #Q9 bulk discount
    if bulk_order and quantity>=10:
        discount=original_total*0.08
    discount_total=original_total-discount
    #Q7 Delivery charges
    if delivery_slot=="Morning":
        delivery_charge=40
    elif delivery_slot=="Evening":
        delivery_charge=60
    else:
        delivery_charge=0
    total=discount_total+delivery_charge
    return {"original_total":original_total,"discount":discount,"final_total":total}

#Q10 using is not None checks
def filter_items_logic(category=None,max_price=None,unit=None,in_stock=None):
    res=items
    if category is not None:
        res=[i for i in res if i["category"].lower()==category.lower()]
    if max_price is not None:
        res=[i for i in res if i["price"]<=max_price]
    if unit is not None:
        res=[i for i in res if i["unit"].lower()==unit.lower()]
    if in_stock is not None:
        res=[i for i in res if i["in_stock"]==in_stock]
    return res

# ----------------HOME ROUTE----------------
#Q1 Creating GET "/"
@app.get("/")
def home():
    return {"message":"Welcome to FreshMart Grocery"}

#Q2 Creating GET "/items"
@app.get("/items")
def get_all_items():
    stock_available=len([i for i in items if i["in_stock"]])
    return {"items":items,"total_items":len(items),"in_stock_count":stock_available}

#Q10 Creating GET "../filter" for items
@app.get("/items/filter")
def filter_items(category:Optional[str]=None,max_price:Optional[int]=None,unit:Optional[str]=None,in_stock:Optional[bool]=None):
    filtered_results=filter_items_logic(category,max_price,unit,in_stock)
    return {"filtered_items":filtered_results,"total_found":len(filtered_results)}

#Q16 Creating GET "../search" for items
@app.get("/items/search")
def search_items(keyword:str):
    results=[i for i in items if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]
    if not results:
        return {"message":f"No items found matching {keyword}","results":[],"total_found":0}
    return {"results":results,"total_found":len(results)}

#Q17 Creating GET "../sort" for items
@app.get("/items/sort")
def sort_items(sort_by:str="price",order:str="asc"):
    if sort_by not in ["price","name","category"]:
        return {"error":"Invalid sort field"}
    if order not in ["asc","desc"]:
        return {"error":"Invalid order"}
    reverse=True if order=="desc" else False
    sorted_items=sorted(items,key=lambda x:x[sort_by],reverse=reverse)
    return {"sorted_items":sorted_items,"sort_by":sort_by,"order":order}

#Q18 Creating GET "../page" for items
@app.get("/items/page")
def paginate_items(page:int=Query(1,ge=1),limit:int=Query(4,ge=1,le=10)):
    total=len(items)
    start=(page-1)*limit
    end=start+limit
    total_pages=(total+limit-1)//limit
    return {"page":page,"limit":limit,"total_items":total,"total_pages":total_pages,"items":items[start:end]}

#Q20 Creating GET "../browse" for items 
@app.get("/items/browse")
def browse_items(keyword:Optional[str]=None,category:Optional[str]=None,in_stock:Optional[bool]=None,sort_by:str="price",order:str="asc",page:int=1,limit:int=4):
    if sort_by not in ["price","name","category"]:
        return {"error":"Invalid sort field"}
    if order not in ["asc","desc"]:
        return {"error":"Invalid order"}
    result=items
    if keyword:
        result=[i for i in result if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]
    if category:
        result=[i for i in result if i["category"].lower()==category.lower()]
    if in_stock is not None:
        result=[i for i in result if i["in_stock"]==in_stock]
    reverse=True if order=="desc" else False
    result=sorted(result,key=lambda x:x[sort_by],reverse=reverse)
    total=len(result)
    start=(page-1)*limit
    end=start+limit
    total_pages=(total+limit-1)//limit
    return {"total":total,"page":page,"total_pages":total_pages,"results":result[start:end]}

#Q5 Creating GET "../summary" for items
@app.get("/items/summary")
def get_inventory_summary():
    stock_available=0
    stock_unavailable=0
    category_map={}
    for product in items:
        if product["in_stock"]:
            stock_available+=1
        else:
            stock_unavailable+=1
        category=product["category"]
        if category in category_map:
            category_map[category]+=1
        else:
            category_map[category]=1
    return {"total_items":len(items),"in_stock_items":stock_available,"out_of_stock_items":stock_unavailable,"category_breakdown":category_map}

#Q3 Creating GET "../item_id"
@app.get("/items/{item_id}")
def get_item_by_id(item_id:int):
    item_record=find_item(item_id)
    if not item_record:
        return {"error":"Item not found"}
    return {"item":item_record}

#Q4 Creating GET "/orders"
@app.get("/orders")
def get_all_orders():
    return {"orders":orders,"total_orders":len(orders)}

#Q19 Creating GET "../search", "../sort and "../page" for orders
@app.get("/orders/search")
def search_orders(customer_name:str):
    results=[o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"results":results,"total_found":len(results)}

@app.get("/orders/sort")
def sort_orders(order:str="asc"):
    if order not in ["asc","desc"]:
        return {"error":"Invalid order"}
    reverse=True if order=="desc" else False
    sorted_orders=sorted(orders,key=lambda x:x["total_cost"],reverse=reverse)
    return {"orders":sorted_orders}

@app.get("/orders/page")
def paginate_orders(page:int=Query(1,ge=1),limit:int=Query(3,ge=1,le=10)):
    total=len(orders)
    start=(page-1)*limit
    end=start+limit
    total_pages=(total+limit-1)//limit
    return {"page":page,"total_pages":total_pages,"orders":orders[start:end]}

#Q8 Creating POST Order
@app.post("/orders")
def create_order(order:OrderRequest):
    global order_counter
    item=find_item(order.item_id)
    if not item:
        return {"error":"Item not found"}
    if not item["in_stock"]:
        return {"error":"Item out of stock"}
    bill=calculate_total(item["price"],order.quantity,order.delivery_slot,order.bulk_order)
    new_order={"order_id":order_counter,"customer_name":order.customer_name,"item_name":item["name"],"quantity":order.quantity,"unit":item["unit"],"delivery_slot":order.delivery_slot,"original_cost":bill["original_total"],"discount":bill["discount"],"total_cost":bill["final_total"],"status":"confirmed"}
    orders.append(new_order)
    order_counter+=1
    return new_order

#Q11 Creating POST "/items"
@app.post("/items",status_code=201)
def add_item(new_item:NewItem):
    for existing in items:
        if existing["name"].lower()==new_item.name.lower():
            return {"error":"Item already exists"}
    new_id=max(i["id"] for i in items)+1
    item_data=new_item.dict()
    item_data["id"]=new_id
    items.append(item_data)
    return item_data

#Q12 Creating PUT "../item_id" for items
@app.put("/items/{item_id}")
def update_item(item_id:int,price:Optional[int]=None,in_stock:Optional[bool]=None):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if price is not None:
        item["price"]=price
    if in_stock is not None:
        item["in_stock"]=in_stock
    return item

#Q13 Creating DELETE "../item_id" for items
@app.delete("/items/{item_id}")
def delete_item(item_id:int):
    item=find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for order in orders:
        if order["item_name"]==item["name"]:
            return {"error":"Item has active orders"}
    items.remove(item)
    return {"message":"Item deleted successfully"}

#Q14 Creating POST "../add" for cart and GET "/cart"
@app.post("/cart/add")
def add_to_cart(item_id:int,quantity:int=1):
    item=find_item(item_id)
    if not item:
        return {"error":"Item not found"}
    if not item["in_stock"]:
        return {"error":"Item out of stock"}
    for c in cart:
        if c["item_id"]==item_id:
            c["quantity"]+=quantity
            return {"message":"Quantity updated","cart":cart}
    cart.append({"item_id":item_id,"name":item["name"],"price":item["price"],"unit":item["unit"],"quantity":quantity})
    return {"message":"Item added","cart":cart}

@app.get("/cart")
def view_cart():
    total=0
    cart_details=[]
    for c in cart:
        subtotal=c["price"]*c["quantity"]
        total+=subtotal
        cart_details.append({**c,"subtotal":subtotal})
    return {"cart":cart_details,"grand_total":total}

#Q15 Creating REMOVE "/item_id" and POST "../checkout" for cart
@app.delete("/cart/{item_id}")
def remove_cart_item(item_id:int):
    for c in cart:
        if c["item_id"]==item_id:
            cart.remove(c)
            return {"message":"Item removed"}
    return {"error":"Item not in cart"}

@app.post("/cart/checkout",status_code=201)
def checkout(data:CheckoutRequest):
    global order_counter
    if not cart:
        return {"error":"Cart is empty"}
    placed_orders=[]
    grand_total=0
    for c in cart:
        bill=calculate_total(c["price"],c["quantity"],data.delivery_slot)
        order={"order_id":order_counter,"customer_name":data.customer_name,"item_name":c["name"],"unit":c["unit"],"quantity":c["quantity"],"delivery_slot":data.delivery_slot,"total_cost":bill["final_total"]}
        grand_total+=bill["final_total"]
        orders.append(order)
        placed_orders.append(order)
        order_counter+=1
    cart.clear()
    return {"orders":placed_orders,"grand_total":grand_total}