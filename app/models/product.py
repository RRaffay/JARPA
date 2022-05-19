from flask import current_app as app
from .user import User

# Class for the Product Table
class Product:
    def __init__(self, pid, name, price,image,description,category,creator_id):
        self.pid = pid
        self.name = name
        self.price = price
        self.image = image
        self.description = description
        self.category = category
        self.creator_id = creator_id
        

# Function which gets a single product given its product id        
    @staticmethod
    def get(pid):
        pid = int(pid)
        rows = app.db.execute('''
SELECT pid, name, price,image,description,category,creator_id
FROM Products
WHERE pid = :pid
''',
                              pid=pid)
        return Product(*(rows[0])) if rows is not None else None

# Function which returns all products in the Product table, ordered by name and then price
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT pid, name, price,image,description,category,creator_id
FROM Products
ORDER BY name, price
''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_by_offset_sort(offset,sort_type,direction):
        offset = "\nLIMIT 10 OFFSET " + str(int(offset))
        order_by = "\nORDER BY " + sort_type + " " + direction
        rows = app.db.execute('''
SELECT pid, name, price,image,description,category,creator_id
FROM Products
''' + order_by + offset)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_number_of_products():
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
''')
        return rows[0][0]

# Funciton which returns all products in a specified category
    @staticmethod
    def get_by_category(required_cat):
        rows = app.db.execute('''
SELECT pid, name, price,image,description,category,creator_id
FROM Products
WHERE category = :required_cat
''',required_cat=required_cat)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_avg_rating(pid):
        rows = app.db.execute("""
        SELECT AVG(rating)
        FROM Reviews_Product
        WHERE product_id = :pid
        """,
                                pid=pid)
        return int(rows[0][0]) if rows[0][0] else 0


    # Only shows products with quantity >= 0. Functions to preserve old order history
    # Function which returns all Products which are sold by a given seller

    @staticmethod
    def sells(uid):
        rows = app.db.execute("""
        SELECT pid, name, price,image,description,category, creator_id
        FROM Products
        WHERE pid IN (
            SELECT pid
            FROM Sells
            WHERE seller_id = :uid
        )
        ORDER BY name ASC
    """,
                                uid=uid)

        q = []
        for product in rows:
            quantity = app.db.execute(
                'SELECT quantity FROM Sells WHERE pid = :pid AND seller_id = :uid',
                pid=product.pid,
                uid=uid
            )[0][0]
            q.append(quantity)
        filter = []
        for i in range(len(rows)):
            if q[i] >= 0:
                filter.append((Product(*rows[i]), q[i]))
        return filter

    # Function for adding a Product to the Product database (used for form)
    @staticmethod
    def addProduct(productName, description, image, price, category, creator_id):
        try:
            rows = app.db.execute("""
    INSERT INTO Products(name, description, image, price, category, creator_id)
    VALUES(:productName, :description, :image, :price, :category, :creator_id)
    RETURNING pid
    """,
                                    productName=productName,
                                    description=description,
                                    image=image,
                                    price=price,
                                    category=category,
                                    creator_id=creator_id)
            pid = rows[0][0]
            print("Product added:", pid, productName, description, image, price, category, creator_id)
            return Product.get(pid)
        except Exception as e:
            # Product could not be added
            print(e)
            return None

    
    @staticmethod
    def updateProduct(productName, description, image, price, category,creator_id):
        try:
            rows = app.db.execute("""
    UPDATE Products
    SET name = :productName, description = :description, image = :image, price = :price, category = :category
    WHERE creator_id = :creator_id
    """,
                                    productName=productName,
                                    description=description,
                                    image=image,
                                    price=price,
                                    category=category,
                                    creator_id=creator_id)
            pid = rows[0][0]
            print("Product Updated:", pid, productName, description, image, price, category, creator_id)
            return
        except Exception as e:
            # Product could not be added
            print(e)
            return None
    
    
    # Function which returns all ratings for a given product (pid)
    @staticmethod
    def ratings(pid):
        reviews = app.db.execute("""
    SELECT rating, review, user_id
    FROM Reviews_Product
    WHERE product_id = :pid
    ORDER BY rating DESC
    """,
                            pid=pid)

        for i in range(len(reviews)):
            reviews[i] = list(reviews[i]) + [User.get_name(reviews[i][2])]
            print(reviews[i])

        return reviews


    # Compare with other methods to see if things need to be added
    @staticmethod
    def seller_update(seller_id, pid, new_quantity):
        try:
            app.db.execute("""
            UPDATE Sells
            SET quantity = :new_quantity
            WHERE seller_id = :seller_id AND pid = :pid
            RETURNING seller_id, pid
            """,
                            seller_id = seller_id,
                            pid = pid,
                            new_quantity = new_quantity)
            return seller_id, pid
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def creator_products(creator_id):
        prods = app.db.execute("""
    SELECT *
    FROM Products
    WHERE creator_id = :creator_id
    """,
                            creator_id=creator_id)

        return [Product(*row) for row in prods]

    # Set quantity = -1 so past order history is not disturbed;
    # Orders table is preserved this way
    @staticmethod
    def seller_remove(seller_id, pid):
        try:
            app.db.execute("""
            UPDATE Sells
            SET quantity = -1
            WHERE seller_id = :seller_id AND pid = :pid
            RETURNING seller_id, pid
            """,
                            seller_id = seller_id,
                            pid = pid)
            return seller_id, pid
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def seller_add(seller_id, pid, quantity):
        try:
            app.db.execute("""
    INSERT INTO Sells(seller_id, pid, quantity)
    VALUES(:seller_id, :pid, :quantity)
    RETURNING seller_id, pid
    """,
                seller_id = seller_id,
                pid = pid,
                quantity = quantity)
            return seller_id, pid
    # Run if a product has previously been in a seller's inventory and they want to readd it
        except Exception as e:
            print(f'\n\n{e}\n\n')
            try:
                app.db.execute("""
                UPDATE Sells
                SET quantity = :quantity
                WHERE seller_id = :seller_id AND pid = :pid AND quantity = -1
                RETURNING seller_id, pid
                """,
                    seller_id = seller_id,
                    pid = pid,
                    quantity = quantity)
            except Exception as e:
                print(f'\n\n{e}\n\n')
                return None

    @staticmethod
    def available_to_add_seller(seller_id, pid):
        rows = app.db.execute("""
        SELECT seller_id, pid, quantity
        FROM Sells
        WHERE seller_id = :seller_id AND pid = :pid AND quantity >= 0
        """,
                    seller_id=seller_id,
                    pid = pid)
        return [len(rows) <= 0, "This product is already in your inventory"]

    # Function which returns the average rating of the reviews of a single product
    @staticmethod
    def get_avg_rating(pid):
        rows = app.db.execute("""
        SELECT AVG(rating)
        FROM Reviews_Product
        WHERE product_id = :pid
        """,
                                pid=pid)
        return int(rows[0][0]) if rows[0][0] else 0

