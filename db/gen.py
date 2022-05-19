from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 1000
num_sells = num_users * 5
num_categories = 100
num_products = 5000
num_purchases = 5000
num_reviews_seller = num_sells * 5
num_reviews_product = num_products * 5
num_orders = 1000
num_has_in_cart = 1000

Faker.seed(0)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    user_ids = []
    used_emails = set()
    with open('db/data/users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['residence']
            balance = 0.0
            while email in used_emails:
                email = fake.email()
            used_emails.add(email)
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
            user_ids.append(uid)
        print(f'{num_users} generated')
    return user_ids

def gen_categories(num_categories):
    categories = set()
    with open('db/data/categories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True)
        for i in range(num_categories):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            name = fake.word()
            if name in categories:
                continue
            writer.writerow([name])
            categories.add(name)
        print(f'{num_categories} generated')
    return list(categories)

def gen_products(num_products, user_ids, categories):
    available_pids = []

    user_ids = []
    with open('db/data/users.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            user_ids.append(row[0])

    with open('db/data/products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.sentence(nb_words=10)
            image = fake.image_url()
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            category = fake.random_element(elements=categories)
            creator_id = fake.random_element(elements=user_ids)
            available_pids.append(pid)
            writer.writerow([pid, name, description, image, price, category, creator_id])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_sells(num_sells, available_pids, user_ids):
    seen = set()
    with open('db/data/sells.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sells...', end=' ', flush=True)
        for id in range(num_sells):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)

            seller_id = fake.random_element(elements=user_ids[:len(user_ids)//3])
            pid = fake.random_element(elements=available_pids)
            quantity = fake.random_int(min=1, max=100)

            while (seller_id, pid) in seen:
                seller_id = fake.random_element(elements=user_ids[:len(user_ids)//3])

            writer.writerow([seller_id, pid, quantity])
            seen.add((seller_id, pid))

        print(f'{num_sells} generated')
    return list(seen)

def gen_reviews_seller(num_reviews_seller, user_ids, seller_ids):
    used = set()
    with open('db/data/reviews_seller.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller reviews...', end=' ', flush=True)
        for id in range(num_reviews_seller):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)

            user_id = fake.random_element(elements=user_ids)
            seller_id = fake.random_element(elements=seller_ids)
            rating = fake.random_int(min=1, max=5)
            review = fake.sentence(nb_words=10)
            date = fake.date_time()

            if (user_id, seller_id) not in used:
                writer.writerow([rating, review, user_id, seller_id, date])
            used.add((user_id, seller_id))

        print(f'{num_reviews_seller} generated')

def gen_reviews_product(num_reviews_product, user_ids, available_pids):
    used = set()
    with open('db/data/reviews_product.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product reviews...', end=' ', flush=True)
        for id in range(num_reviews_product):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)

            user_id = fake.random_element(elements=user_ids)
            product_id = fake.random_element(elements=available_pids)
            rating = fake.random_int(min=1, max=5)
            review = fake.sentence(nb_words=10)
            date = fake.date_time()

            if (user_id, product_id) not in used:
                writer.writerow([rating, review, user_id, product_id, date])
            used.add((user_id, product_id))
        print(f'{num_reviews_product} generated')
            
def gen_orders(num_orders, user_ids, ids_pids, seller_ids):

    seen = set()

    with open('db/data/orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for id in range(num_orders):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
        
            user_id = fake.random_element(elements=user_ids)
            seller_id = fake.random_element(elements=seller_ids)

            available_pids = [pid[1] for pid in ids_pids if pid[0] == seller_id]

            pid = fake.random_element(elements=available_pids)

            

            num_items = fake.random_int(min=1, max=100)
            fulfilled = fake.random_element(elements=('true', 'false'))
            date = fake.date_time()
            if (id//8, pid) not in seen:
                seen.add((id//8, pid))         
                writer.writerow([id//8, pid, user_id, seller_id, date, fulfilled, num_items])

        print(f'{num_orders} generated')

def gen_has_in_cart(num_has_in_cart, user_ids, available_pids):
    used = set()
    with open('db/data/has_in_cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Has in cart...', end=' ', flush=True)
        for id in range(num_has_in_cart):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            
            user_id = fake.random_element(elements=user_ids)
            pid = fake.random_element(elements=available_pids)
            quantity = fake.random_int(min=1, max=100)
            if (user_id, pid) not in used:
                writer.writerow([user_id, quantity, pid, 0])
            used.add((user_id, pid))
        print(f'{num_has_in_cart} generated')

def gen_coupons():
    with open('db/data/coupons.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Coupons...', end=' ', flush=True)
        for i in range(100):
            code = fake.sentence(nb_words=1)[:-1].upper()
            discount = fake.random_int(min=1, max=50)
            print(code, discount)
            writer.writerow([i, code, discount])
        
user_ids = gen_users(num_users)
categories = gen_categories(num_purchases)
available_pids = gen_products(num_products, user_ids, categories)
ids_pids = gen_sells(num_sells, available_pids, user_ids)
seller_ids = [id_pid[0] for id_pid in ids_pids]
gen_reviews_seller(num_reviews_seller, user_ids, seller_ids)
gen_reviews_product(num_reviews_product, user_ids, available_pids)
gen_orders(num_orders, user_ids, ids_pids, seller_ids)
gen_has_in_cart(num_has_in_cart, user_ids, available_pids)
gen_coupons()