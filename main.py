import pymongo,datetime,os,re
import bcrypt
from flask import Flask, request, render_template, redirect, session
from bson import ObjectId
from bson import ObjectId
from flask import flash
from bson.errors import InvalidId
from urllib.parse import urlencode

my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_database = my_client["FoodTruckProject"]

admin_collection = my_database["admin"]
category_collection = my_database["category"]
customers_collection = my_database["customers"]
delivery_boys_collection = my_database["delivery_boys"]
food_truck_collection = my_database["food_truck"]
locations_collection = my_database["locations"]
menu_collection = my_database["menu"]
orders_collection = my_database["orders"]
payments_collection = my_database["payments"]
timings_collection = my_database["timings"]

app = Flask(__name__)
app.secret_key = "adhi-dha-surprise"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = APP_ROOT + "/static/images"

admin_username = "admin"
admin_password = "admin"

count = admin_collection.count_documents({"admin_username":admin_username,"admin_password":admin_password})
if count==0:
    admin_collection.insert_one({"admin_username":admin_username,"admin_password":admin_password})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message")
def message():
    return render_template("message.html")

@app.route("/admin_message")
def admin_message():
    return render_template("admin_message.html")

@app.route("/customer_message")
def customer_message():
    return render_template("customer_message.html")

@app.route("/delivery_boy_message")
def delivery_boy_message():
    return render_template("delivery_boy_message.html")

@app.route("/food_truck_message")
def food_truck_message():
    return render_template("food_truck_message.html")

@app.route("/location_message")
def location_message():
    return render_template("location_message.html")

@app.route("/cancel_order_message")
def cancel_order_message():
    return render_template("cancel_order_message.html")

@app.route("/wrong_order_message")
def wrong_order_message():
    return render_template("wrong_order_message.html")

@app.route("/uos_message")
def uos_message():
    return render_template("uos_message.html")

@app.route("/final_order_message")
def final_order_message():
    return render_template("final_order_message.html")

@app.route("/orders_message")
def orders_message():
    return render_template("orders_message.html")

@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    count = admin_collection.count_documents({"admin_username": username, "admin_password": password})
    if count > 0:
        session["role"] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("admin_message.html", message="Invalid Login Credentials")

@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")

@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    query = {"email": email, "password": password}
    count = customers_collection.count_documents(query)
    if count > 0:
        customer = customers_collection.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = 'customer'
        return redirect("/customer_home")
    else:
        return render_template("customer_message.html", message="Invalid Login Credentials")


@app.route("/customer_registeration")
def customer_registeration():
    return render_template("customer_registeration.html")


@app.route("/customer_registeration_action", methods=['POST'])
def customer_registeration_action():
    name1 = request.form.get("name1")
    name2 = request.form.get("name2")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    dob = request.form.get("dob")
    address = request.form.get("address")
    state = request.form.get("state")
    city = request.form.get("city")
    zipcode = request.form.get("zipcode")

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect("/customer_registeration")

    if customers_collection.count_documents({"email": email}) > 0:
        flash("Duplicate Email Address", "error")
        return redirect("/customer_registeration")

    if customers_collection.count_documents({"phone": phone}) > 0:
        flash("Duplicate Phone Number", "error")
        return redirect("/customer_registeration")
    
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_customer = {"name1": name1,"name2": name2,"email": email,"phone": phone,"password": password,"encrypted_password":encrypted_password,"dob": dob,"address": address,"state": state,"city": city,"zipcode": zipcode}
    customers_collection.insert_one(new_customer)
    flash("Customer Registered Successfully!", "success")
    return redirect("/customer_registeration")


@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")


@app.route("/add_food_truck")
def add_food_truck():
    query = {}
    food_truck = food_truck_collection.find(query)
    food_trucks = list(food_truck)
    return render_template("add_food_truck.html",food_trucks=food_trucks)


@app.route("/add_food_truck_action", methods=['post'])
def add_food_truck_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    food_truck_category = request.form.get("food_truck_category")

    query = {"email": email}
    count = food_truck_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    query = {"phone": phone}
    count = food_truck_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_food_truck = {"name": name,"email": email,"phone": phone,"password": password,"encrypted_password": encrypted_password,"address": address,"city": city,"state": state,"zipcode": zipcode,"food_truck_category": food_truck_category,"first_login": True}
        
    food_truck_collection.insert_one(new_food_truck)
    return redirect("/add_food_truck")


@app.route("/food_truck_first_login")
def food_truck_first_login():
    return render_template("food_truck_first_login.html")

@app.route("/food_truck_first_login_action", methods=['POST'])
def food_truck_first_login_action():
    food_truck_id = session['food_truck_id']
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New password and confirm password do not match", "error")
        return redirect("/food_truck_first_login")
        
    food_truck = food_truck_collection.find_one({"_id": ObjectId(food_truck_id)})
    if food_truck and food_truck["password"] == current_password:
        food_truck_collection.update_one(
            {"_id": ObjectId(food_truck_id)}, 
            {"$set": {"password": new_password, "first_login": False}}
        )
        flash("Password changed successfully", "success")
        return redirect("/add_menu")
    else:
        flash("Current password is incorrect", "error")
        return redirect("/food_truck_first_login")


@app.route("/food_truck_login")
def food_truck_login():
    return render_template("food_truck_login.html")


@app.route("/food_truck_login_action", methods=['post'])
def food_truck_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    query = {"email": email, "password": password}
    count = food_truck_collection.count_documents(query)
    if count > 0:
        food_truck = food_truck_collection.find_one(query)
        session['food_truck_id'] = str(food_truck['_id'])
        session['role'] = 'food_truck'
        if food_truck.get('first_login', False):
            flash("Please change your password for security reasons", "info")
            return redirect("/food_truck_first_login")
        else:
            return redirect("/add_menu")
    else:
        return render_template("error_message.html", message="Invalid Login Credentials")


@app.route("/food_truck_change_password")
def food_truck_change_password():
    return render_template("food_truck_change_password.html")


@app.route("/food_truck_change_password_action", methods=['POST'])
def food_truck_change_password_action():
    food_truck_id = session['food_truck_id']
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New password and confirm password do not match","error")
        return redirect("/food_truck_change_password")
    food_truck = food_truck_collection.find_one({"_id": ObjectId(food_truck_id)})
    if food_truck and food_truck["password"] == current_password:
        food_truck_collection.update_one({"_id": ObjectId(food_truck_id)}, {"$set":{"password": new_password}})
        flash("Password changed successfully","success")
    else:
        flash("Current password is incorrect","error")
    return redirect("/food_truck_change_password")


@app.route("/food_truck_home")
def food_truck_home():
    return render_template("food_truck_home.html")


@app.route("/food_truck_profile")
def food_truck_profile():
    food_truck_id = session['food_truck_id']
    query={ "_id": ObjectId(food_truck_id)}
    food_truck = food_truck_collection.find_one(query)
    print(food_truck)
    return render_template("food_truck_profile.html", food_truck=food_truck)


@app.route("/add_delivery_boy")
def add_delivery_boy():
    query = {}
    delivery_boys = list(delivery_boys_collection.find(query))
    print(delivery_boys)
    return render_template("add_delivery_boy.html", delivery_boys=delivery_boys)


@app.route("/add_delivery_boy_action", methods=['post'])
def add_delivery_boy_action():
    name1 = request.form.get("name1")
    name2 = request.form.get("name2")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")

    query = {"email": email}
    count = delivery_boys_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")

    query = {"phone": phone}
    count = delivery_boys_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    query = {"name1": name1, "name2": name2, "email": email, "phone": phone, "password":password,"encrypted_password":encrypted_password, "address": address,"city": city,"state": state,"zipcode": zipcode,"first_login": True}
    delivery_boys_collection.insert_one(query)
    return redirect("/add_delivery_boy")



@app.route("/delivery_boy_first_login")
def delivery_boy_first_login():
    return render_template("delivery_boy_first_login.html")

@app.route("/delivery_boy_first_login_action", methods=['POST'])
def delivery_boy_first_login_action():
    delivery_boy_id = session['delivery_boy_id']
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New password and confirm password do not match", "error")
        return redirect("/delivery_boy_first_login")

    delivery_boy = delivery_boys_collection.find_one({"_id": ObjectId(delivery_boy_id)})

    if delivery_boy and delivery_boy["password"] == current_password:
        delivery_boys_collection.update_one(
            {"_id": ObjectId(delivery_boy_id)},
            {"$set": {"password": new_password, "first_login": False}}
        )
        flash("Password changed successfully", "success")
        return redirect("/delivery_boy_home")
    else:
        flash("Current password is incorrect", "error")
        return redirect("/delivery_boy_first_login")

@app.route("/delivery_boy_login")
def delivery_boy_login():
    return render_template("delivery_boy_login.html")


@app.route("/delivery_boy_login_action", methods=['post'])
def delivery_boy_login_action():
    email = request.form.get("email")
    password = request.form.get("password")

    query = {"email": email, "password": password}
    delivery_boy = delivery_boys_collection.find_one(query)

    if delivery_boy:
        session['delivery_boy_id'] = str(delivery_boy['_id'])
        session['role'] = 'delivery_boys'

        # 👇 Redirect to first login change password page
        if delivery_boy.get('first_login', False):
            flash("Please change your password for security reasons", "info")
            return redirect("/delivery_boy_first_login")
        return redirect("/delivery_boy_home")
    else:
        return render_template("error_message.html", message="Invalid Login Details")

@app.route("/delivery_boy_home")
def delivery_boy_home():
    timings = request.form.get("timings")
    query = {"$or": [{"status": 'Dispatched'}, {"status": 'DeliveryBoy Assigned'}]}
    orders = list(orders_collection.find(query))
    delivery_boys = list(delivery_boys_collection.find())
    order_date = datetime.datetime.now()
    order_date = order_date.strftime("%Y-%m-%d")
    return render_template("delivery_boy_home.html", timings=timings, get_delivery_boys=get_delivery_boys, delivery_boys=delivery_boys, orders=orders, get_order_items_id_by_order_id=get_order_items_id_by_order_id, get_customer_name_by_customer=get_customer_name_by_customer, get_menu_price_by_menu_id=get_menu_price_by_menu_id, get_food_truck_name_by_food_truck_id=get_food_truck_name_by_food_truck_id, int=int, float=float, order_date=order_date, get_timings_by_food_truck_id_and_order_date=get_timings_by_food_truck_id_and_order_date, get_location_by_location_id=get_location_by_location_id)


@app.route("/delivery_boy_profile")
def delivery_boy_profile():
    delivery_boy_id = session['delivery_boy_id']
    query = {"_id": ObjectId(delivery_boy_id)}
    delivery_boy = delivery_boys_collection.find_one(query)
    print(delivery_boy)
    return render_template("delivery_boy_profile.html",delivery_boy=delivery_boy)


@app.route("/delivery_boy_change_password")
def delivery_boy_change_password():
    return render_template("delivery_boy_change_password.html")


@app.route("/delivery_boy_change_password_action", methods=['POST'])
def delivery_boy_change_password_action():
    delivery_boy_id = session['delivery_boy_id']
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New password and confirm password do not match","error")
        return redirect("/delivery_boy_change_password")
    delivery_boy = delivery_boys_collection.find_one({"_id": ObjectId(delivery_boy_id)})
    if delivery_boy and delivery_boy["password"] == current_password:
        delivery_boys_collection.update_one({"_id": ObjectId(delivery_boy_id)}, {"$set":{"password": new_password}})
        flash("Password changed successfully","success")
    else:
        flash("Current password is incorrect","error")
    return redirect("/delivery_boy_change_password")


@app.route("/add_category")
def add_category():
    category = list(category_collection.find())
    return render_template("add_category.html", category=category)


@app.route("/add_category_action", methods=['post'])
def add_category_action():
    category_name = request.form.get("category_name")
    query = {"category_name": category_name}
    count = category_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Category Name")
    category_collection.insert_one(query)
    return redirect("/add_category")
    # return render_template("message.html", message="Category Added Successfully")


@app.route("/add_locations")
def add_locations():
    query = {}
    locations = list(locations_collection.find(query))
    print(locations)
    return render_template("add_locations.html", locations=locations)


@app.route("/add_locations_action", methods=['post'])
def add_locations_action():
    location_name = request.form.get("location_name")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")
    query = {"location_name":location_name}
    count = locations_collection.count_documents(query)
    if count >0:
        return render_template("message.html", message="Duplicate Location Expected")
    else:
        query = {"location_name": location_name, "address": address, "state": state, "city": city, "zipcode": zipcode}
        locations_collection.insert_one(query)
        return redirect("/add_locations")
        # return render_template("location_message.html", message="location Added")


@app.route("/update_truck_timings")
def update_truck_timings():
    food_truck_id = session['food_truck_id']
    locations = list(locations_collection.find({}))
    timings = list(timings_collection.find({"food_truck_id": ObjectId(food_truck_id)}))
    return render_template("update_truck_timings.html",locations=locations,timings=timings,get_location_by_location_ids=get_location_by_location_ids)


@app.route("/update_truck_timings_action", methods=['POST'])
def update_truck_timings_action():
    location_id = request.form.get("location_id")
    food_truck_id = session['food_truck_id']
    day = request.form.get("day")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    start_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")
    query = {"day": day,"start_time": start_time,"end_time": end_time,"location_id": ObjectId(location_id),"food_truck_id": ObjectId(food_truck_id)}
    timings_collection.insert_one(query)
    return redirect("/update_truck_timings")


@app.route("/add_menu")
def add_menu():
    query = {}
    categorys = list(category_collection.find(query))
    food_truck_id = session['food_truck_id']
    keyword = request.args.get("keyword", "")
    keyword2 = re.compile(".*" + str(keyword) + ".*", re.IGNORECASE)
    query = {"food_truck_id": ObjectId(food_truck_id), "food_name": keyword2}
    menus = list(menu_collection.find(query))
    return render_template("add_menu.html", menus=menus, categorys=categorys)


@app.route("/add_menu_action", methods=['POST'])
def add_menu_action():
    category_id = request.form.get("category_id")
    food_truck_id = session['food_truck_id']
    food_name = request.form.get("food_name")
    price = request.form.get("price")
    description = request.form.get("description")
    image = request.files.get("image")
    path = IMAGES_PATH + "/" + image.filename
    image.save(path)
    query = {"food_name": food_name,"image": image.filename,"price": price,"description": description,"food_truck_id": ObjectId(food_truck_id),"category_id": ObjectId(category_id)}
    menu_collection.insert_one(query)
    return redirect("/add_menu")


@app.route("/edit_menu/<menu_id>")
def edit_menu(menu_id):
    menu = menu_collection.find_one({"_id": ObjectId(menu_id)})
    categorys = list(category_collection.find({}))
    return render_template("edit_menu.html", menu=menu, categorys=categorys)


@app.route("/update_menu/<menu_id>", methods=['POST'])
def update_menu(menu_id):
    food_name = request.form.get("food_name")
    price = request.form.get("price")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    image = request.files.get("image")
    update_data = {"food_name": food_name,"price": price,"description": description,"category_id": ObjectId(category_id)}
    if image and image.filename != "":
        path = IMAGES_PATH + "/" + image.filename
        image.save(path)
        update_data["image"] = image.filename
    menu_collection.update_one({"_id": ObjectId(menu_id)}, {"$set": update_data})
    return redirect("/add_menu")


@app.route("/view_menu")
def view_menu():
    query = {}
    keyword = request.args.get("keyword", "")
    food_truck_id = request.args.get("food_truck_id")
    category_id = request.args.get("category_id")
    timing = None
    keyword_regex = re.compile(".*" + str(keyword) + ".*", re.IGNORECASE)
    query["food_name"] = keyword_regex

    if session['role'] == 'food_truck':
        food_truck_id = session['food_truck_id']
        query["food_truck_id"] = ObjectId(food_truck_id)

    elif session['role'] == 'customer':
        if food_truck_id:
            today = datetime.datetime.now()
            day = today.strftime("%A")
            time = datetime.datetime.strptime(today.strftime("%H:%M"), "%H:%M")
            timing_query = {"day": day,"food_truck_id": ObjectId(food_truck_id),"start_time": {"$lte": time},"end_time": {"$gte": time}}
            timing = timings_collection.find_one(timing_query)

            if timing:
                query["food_truck_id"] = ObjectId(food_truck_id)
            else:
                query["food_truck_id"] = ObjectId("000000000000000000000000")

        if category_id:
            query["category_id"] = ObjectId(category_id)
    menus = list(menu_collection.find(query))
    food_trucks = list(food_truck_collection.find({}))
    categorys = list(category_collection.find({}))

    return render_template("view_menu.html",menus=menus,categorys=categorys,food_trucks=food_trucks,food_truck_id=food_truck_id,category_id=category_id,keyword=keyword,str=str,timing=timing)


def get_order_by_order_id(order_id):
    query = {"_id": ObjectId(order_id)}
    order = orders_collection.find_one(query)
    return order

def get_category_name_by_category(category_id):
    query = {"_id": ObjectId(category_id)}
    category = category_collection.find_one(query)
    return category

def get_food_truck_name_by_food_truck_id(food_truck_id):
    food_truck = food_truck_collection.find_one({"_id": ObjectId(food_truck_id)})
    return food_truck

def get_customer_name_by_customer(customer_id):
    customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
    return customer

def get_order_items_id_by_order_id(order_id):
    order_items = orders_collection.find({"_id": ObjectId(order_id)})
    return list(order_items)

def get_menu_price_by_menu_id(menu_id):
    print(menu_id)
    query = {"_id": menu_id}
    menu = menu_collection.find_one(query)
    return menu

def get_delivery_boys():
    delivery_boys = list(delivery_boys_collection.find())
    return delivery_boys

def get_menu_by_menu_id(menu_id):
    query = {"menu_id": str(menu_id)}
    return menu_collection.find_one(query)


def get_timings_by_food_truck_id_and_order_date(food_truck_id, order_date):
    order_date = datetime.datetime.strptime(order_date, "%Y-%m-%d")
    day = order_date.strftime("%A")
    query = {"day": day, "food_truck_id": food_truck_id}
    timings = timings_collection.find(query)
    timings = list(timings)
    return timings

def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    location = locations_collection.find_one(query)
    print(location)
    return location

def get_location_by_location_ids(location_id):
    return locations_collection.find_one({"_id": ObjectId(location_id)})


@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    quantity = request.form.get("quantity")
    menu_id = request.form.get("menu_id")
    menu = menu_collection.find_one({'_id': ObjectId(menu_id)})
    food_truck_id = menu['food_truck_id']
    customer_id = session['customer_id']

    query = {"customer_id": ObjectId(customer_id), "status": "Cart", "food_truck_id": ObjectId(food_truck_id)}
    count = orders_collection.count_documents(query)
    if count == 0:
        result = orders_collection.insert_one({"customer_id": ObjectId(customer_id),"status": "Cart","date": datetime.datetime.now(),"food_truck_id": ObjectId(food_truck_id)})
        order_id = result.inserted_id
    else:
        orders = orders_collection.find_one(query)
        order_id = orders['_id']

    count = orders_collection.count_documents({"order_items.menu_id": ObjectId(menu_id), "_id": order_id})
    if count == 0:
        order_item = {"menu_id": ObjectId(menu_id), "quantity": int(quantity)}
        orders_collection.update_one({"_id": order_id}, {"$push": {"order_items": order_item}})
        flash("Item added to cart!", "success")
    else:
        query = {"_id": order_id, "order_items.menu_id": ObjectId(menu_id)}
        query2 = {"$inc": {"order_items.$.quantity": int(quantity)}}
        orders_collection.update_one(query, query2)
        flash("Item quantity updated in cart!", "info")

    return redirect("/view_menu")


@app.route("/view_cart")
def view_cart():
    status = request.args.get("status")
    timings = request.form.get("timings")
    query = {}
    if session['role'] == 'customer':
        customer_id = session['customer_id']
        if status == "Cart":
            query = {"status":'Cart', "customer_id": ObjectId(customer_id)}
        elif status == "Ordered":
            query = {"$or":[{"status":'Preparing'},{"status":'Ordered'},{"status":'DeliveryBoy Assigned'},{"status":'Prepared'},{"status":'Dispatched'}, {"status":'Accepted by Delivery Boy'}], "customer_id": ObjectId(customer_id)}
        elif status == 'History':
            query = {"$or":[{"status":'Delivered'},{"status":'Cancelled'},{"status":'Refunded'}], "customer_id": ObjectId(customer_id)}

    elif session['role'] == 'food_truck':
        food_truck_id = session['food_truck_id']
        if status == "Ordered":
            query = {"$or": [{"status": 'Preparing'}, {"status": 'Ordered'}, {"status": 'Prepared'}],"food_truck_id": ObjectId(food_truck_id)}
        elif status == 'Dispatched':
            query = {"$or": [{"status": 'Dispatched'}, {"status": 'DeliveryBoy Assigned'}],"food_truck_id": ObjectId(food_truck_id)}
        elif status == 'History':
            query = {"$or": [{"status": 'Delivered'}, {"status": 'Cancelled'}], "food_truck_id": ObjectId(food_truck_id)}

    elif session['role'] == 'delivery_boys':
        delivery_boy_id = session['delivery_boy_id']
        if status == 'Dispatched':
            query = {"$or": [{"status": 'Dispatched'}, {"status": 'DeliveryBoy Assigned'}, {"status":'Accepted by Delivery Boy'}], "delivery_boy_id": ObjectId(delivery_boy_id)}
        elif status == 'History':
            query = {"$or": [{"status": 'Delivered'}, {"status": 'Cancelled'}], "delivery_boy_id": ObjectId(delivery_boy_id)}

    orders = list(orders_collection.find(query))
    delivery_boys = list(delivery_boys_collection.find())
    order_date = datetime.datetime.now()
    order_date = order_date.strftime("%Y-%m-%d")
    timings = timings_collection.find()
    return render_template("view_cart.html",status=status,timings=timings, get_delivery_boys=get_delivery_boys, delivery_boys=delivery_boys, orders=orders, get_order_items_id_by_order_id=get_order_items_id_by_order_id, get_customer_name_by_customer=get_customer_name_by_customer, get_menu_price_by_menu_id=get_menu_price_by_menu_id, get_food_truck_name_by_food_truck_id=get_food_truck_name_by_food_truck_id, int=int, float=float, order_date=order_date, get_timings_by_food_truck_id_and_order_date=get_timings_by_food_truck_id_and_order_date, get_location_by_location_id=get_location_by_location_id, get_timing_by_id=get_timing_by_id)


@app.route("/add_quantity")
def add_quantity():
    order_id = request.args.get("order_id")
    menu_id = request.args.get("menu_id")
    orders = orders_collection.find_one({"_id": ObjectId(order_id)},{"order_items": {"$elemMatch": {"menu_id": ObjectId(menu_id)}}})

    if not orders or not orders.get('order_items'):
        return redirect("/view_cart?status=Cart")

    order_item = orders['order_items'][0]
    current_quantity = int(order_item['quantity'])

    if current_quantity < 100:
        new_quantity = current_quantity + 1
        orders_collection.update_one({"_id": ObjectId(order_id),"order_items.menu_id": ObjectId(menu_id)},{"$set": {"order_items.$.quantity": new_quantity}})
    return redirect("/view_cart?status=Cart")


@app.route("/remove_quantity")
def remove_quantity():
    order_id = request.args.get("order_id")
    menu_id = request.args.get("menu_id")
    orders = orders_collection.find_one({"_id": ObjectId(order_id)},{"order_items": {"$elemMatch": {"menu_id": ObjectId(menu_id)}}})
    if not orders or not orders.get('order_items'):
        return redirect("/view_cart?status=Cart")
    order_item = orders['order_items'][0]
    current_quantity = int(order_item['quantity'])
    if current_quantity > 1:
        new_quantity = current_quantity - 1
        orders_collection.update_one({"_id": ObjectId(order_id),"order_items.menu_id": ObjectId(menu_id)},{"$set": {"order_items.$.quantity": new_quantity}})
    return redirect("/view_cart?status=Cart")


@app.route("/remove_from_cart")
def remove_from_cart():
    order_id = request.args.get("order_id")
    menu_id = request.args.get("menu_id")
    orders_collection.update_one(  {"_id": ObjectId(order_id)},{"$pull": {"order_items": {"menu_id": ObjectId(menu_id)}}})
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order['order_items']:orders_collection.delete_one({"_id": ObjectId(order_id)})
    return redirect("/view_cart?status=Cart")


@app.route("/cancel_order")
def cancel_order():
    order_id = request.args.get("order_id")
    total_price = request.args.get("total_price")
    query = {"order_id": ObjectId(order_id)}
    payment = payments_collection.find_one(query)
    refund_amount = float(payment['amount']) * 0.9
    food_truck_share = float(payment['amount']) * 0.1
    payments_collection.update_one(query, {"$set": {"status": "Cancelled", "refund_amount": refund_amount, "food_truck_share": food_truck_share}})
    query1 = {"_id": ObjectId(order_id)}
    query2 = {"$set":  {"status":"Cancelled", "refund_amount":refund_amount, "food_truck_share":food_truck_share}}
    orders_collection.update_one(query1, query2)
    return render_template("cancel_order_message.html",payment=payment, total_price=total_price,refund_amount=refund_amount,food_truck_share=food_truck_share, order_id=order_id,float=float, message="Your Order Was Cancelled")


@app.route("/wrong_order_refund")
def wrong_order_refund():
    order_id = request.args.get("order_id")
    total_price = float(request.args.get("total_price"))
    orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": "Refunded"}})
    payments_collection.update_one({"order_id": ObjectId(order_id)}, {"$set": {"status": "Refunded", "refund_amount": total_price, "food_truck_share": 0.0}})
    return render_template("wrong_order_message.html",total_price=total_price,refund_amount=total_price,order_id=order_id,message="Your Refund Was Processed for the Wrong Order")


@app.route("/update_order_status")
def update_order_status():
    order_id = request.args.get("order_id")
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    status = request.args.get("status")

    if (order['order_type'] == 'Pick-up' and 
        order['status'] == 'Prepared' and 
        status == 'Dispatched'):
        
        if 'pickup_time' not in order:
            return redirect("/view_cart?status=Ordered&message=Cannot mark as ready for pickup: Customer has not selected pickup time")
    orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}}) 
    
    if status == 'DeliveryBoy Assigned' and order['order_type'] == 'Delivery':
        pass
    status_messages = {
        "Preparing": "Your Order is Preparing",
        "Prepared": "Your Order is Prepared",
        "Dispatched": "Your Order is Ready To pick-up",
        "Cancelled": "Your Order is Cancelled",
        "Refunded": "Your Order is Refunded",
        "DeliveryBoy Assigned": "Order Prepared & Delivery Boy Assigned"
    }
    
    message = status_messages.get(status, "Order status updated")
    params = {'status': 'Ordered', 'message': message}
    return redirect(f"/view_cart?{urlencode(params)}")


@app.route("/update_pickup_time", methods=["POST"])
def update_pickup_time():
    order_id = request.form.get("order_id")
    pickup_time = request.form.get("pickup_time")
    orders_collection.update_one({"_id": ObjectId(order_id)},{"$set": {"pickup_time": pickup_time}})
    return redirect("/view_cart?status=Ordered&message=Your pickup time has been confirmed")


@app.route("/accept_order", methods=['post'])
def accept_order():
    order_id = request.form.get("order_id")
    delivery_boy_id = session['delivery_boy_id']
    
    query = {"$set": {"status": "Accepted by Delivery Boy", "delivery_boy_id": ObjectId(delivery_boy_id)}}
    orders_collection.update_one({"_id": ObjectId(order_id)}, query)
    
    return render_template("orders_message.html", message="You have accepted the order")

@app.route("/order_collected", methods=['post'])
def order_collected():
    order_id = request.form.get("order_id")
    query = {"$set": {"status": "Delivered"}}
    orders_collection.update_one({"_id": ObjectId(order_id)}, query)
    return redirect("/view_cart?status=History&message=Order has been delivered")

@app.route("/dispatched_update")
def dispatched_update():
    order_id = request.args.get("order_id")
    query = {"$set":{"status":'Delivered'}}
    orders_collection.update_one({"_id":ObjectId(order_id)},query)
    return redirect("/view_cart?status=History&message=Order Delivered")

@app.route("/assign_delivery_boy")
def assign_delivery_boy():
    order_id = request.args.get("order_id")
    query = {}
    delivery_boy = delivery_boys_collection.find(query)
    orders_collection.update_one({"_id":ObjectId(order_id)},query)
    return render_template("message.html",message="Assigned To Delivery Boy")

@app.route("/assign_now_update")
def assign_now_update():
    order_id = request.args.get("order_id")
    query = {"$set":{"status":'Dispatched'}}
    orders_collection.update_one({"_id":ObjectId(order_id)},query)
    return render_template("message.html",message="Order Dispatched")


@app.route("/payment_page")
def payment_page():
    order_id = request.args.get("order_id")
    customer_id = request.args.get("customer_id")
    total_price = request.args.get("total_price")
    return render_template("payment_page.html", total_price=total_price, order_id=order_id,customer_id=customer_id)





@app.route("/payment_page2")
def payment_page2():
    customer_id = session['customer_id']
    orders = orders_collection.find({"status":'Cart',"customer_id":ObjectId(session['customer_id'])})
    total_price=0
    for order in orders:
        for order_item in order['order_items']:
            menu = menu_collection.find_one({"_id":ObjectId(order_item['menu_id'])})
            total_price = float(total_price)+float(order_item['quantity'])*float(menu['price'])
    return render_template("payment_page2.html", total_price=total_price,customer_id=customer_id)



@app.route("/payment_page_action2", methods=['POST'])
def payment_page_action2():
    customer_id = session['customer_id']
    order_type = request.form.get("order_type")
    total_price = request.form.get('total_price')
    payment_method = request.form.get('payment_method')
    card_holder_name = request.form.get('card_holder_name')
    card_number = request.form.get('card_number')
    cvv = request.form.get('cvv')
    expiry_date = request.form.get('expiry_date')
    timings_id = request.form.get('timings_id')
    delivery_boy_id = request.form.get('delivery_boy_id')
    payment_date = datetime.datetime.now()

    orders = orders_collection.find({"status": 'Cart', "customer_id": ObjectId(customer_id)})
    for order in orders:
        payments = {"card_holder_name": card_holder_name, "card_number": card_number, "payment_date": payment_date,
                    "amount": total_price, "payment_method": payment_method, "cvv": cvv, "expiry_date": expiry_date,
                    "status": "Payment Success", "order_id": ObjectId(order['_id']), "customer_id": ObjectId(customer_id)}
        payments_collection.insert_one(payments)
        count = payments_collection.count_documents({"order_id": ObjectId(order['_id'])})
        if count > 0:
            orders_collection.update_one({"_id": ObjectId(order['_id'])}, {"$set": {"status": "Ordered"}})
        query = {"$set": {"status": "Ordered","total_price": total_price,"order_type": order_type,"timings_id": ObjectId(timings_id),"customer_id": ObjectId(customer_id)}}
        orders_collection.update_many({"customer_id": ObjectId(customer_id)}, query)

    return render_template("payment_message.html", message="Payment Successful")



@app.route("/payment_page_action", methods=['POST'])
def payment_page_action():
    order_id = request.form.get('order_id')
    customer_id = session['customer_id']
    order_type = request.form.get("order_type")
    total_price = request.form.get('total_price')
    payment_method = request.form.get('payment_method')
    card_holder_name = request.form.get('card_holder_name')
    card_number = request.form.get('card_number')
    cvv = request.form.get('cvv')
    expiry_date = request.form.get('expiry_date')
    timings_id = request.form.get('timings_id')
    delivery_boy_id = request.form.get('delivery_boy_id')

    query = {"$set": {"status": "Ordered","total_price": total_price,"order_type": order_type,"timings_id": ObjectId(timings_id),"customer_id": ObjectId(customer_id)}}
    orders_collection.update_one({"_id": ObjectId(order_id)}, query)
    payment_date = datetime.datetime.now()
    payments = {"card_holder_name": card_holder_name,"card_number": card_number,"payment_date": payment_date,"amount": total_price,"payment_method": payment_method,"cvv": cvv,"expiry_date": expiry_date,"status": "Payment Success","order_id": ObjectId(order_id),"customer_id": ObjectId(customer_id)}
    payments_collection.insert_one(payments)
    count = payments_collection.count_documents({"order_id": ObjectId(order_id)})
    if count > 0:
        orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": "Ordered"}})
    return render_template("payment_message.html", message="Payment Successful")


@app.route("/view_payment_page")
def view_payment_page():
    order_id = request.args.get("order_id")
    print(order_id)
    total_price = request.args.get("total_price")
    refund_amount = request.args.get("refund_amount")
    food_truck_share = request.args.get("food_truck_share")
    payment = payments_collection.find_one({"order_id": ObjectId(order_id)})
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    return render_template("view_payment_page.html", payment=payment,order=order,total_price=total_price,order_id=order_id,get_order_by_order_id=get_order_by_order_id,get_customer_name_by_customer=get_customer_name_by_customer,refund_amount=refund_amount,food_truck_share=food_truck_share)


@app.route("/get_food_truck_timings")
def get_food_truck_timings():
    order_id = request.args.get("order_id")
    order_date = request.args.get("order_date")
    query = {"_id": ObjectId(order_id)}
    order = orders_collection.find_one(query)
    order_date = datetime.datetime.strptime(order_date, "%Y-%m-%d")
    day = order_date.strftime("%A")
    query = {"day": day, "food_truck_id": ObjectId(order['food_truck_id'])}
    timings = timings_collection.find(query)
    timings = list(timings)
    return render_template("get_food_truck_timings.html", timings=timings, get_location_by_location_id=get_location_by_location_id)
def get_timing_by_id(timing_id):
    return timings_collection.find_one({"_id": ObjectId(timing_id)})

@app.route("/change_pickup_location", methods=["POST"])
def change_pickup_location():
    order_id = request.form.get("order_id")
    timings_id = request.form.get("timings_id")

    # Update the order with the new selected timings_id
    orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"timings_id": ObjectId(timings_id)}}
    )

    return redirect("/view_cart?status=Ordered&message=Pickup location changed successfully")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")  
app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)



