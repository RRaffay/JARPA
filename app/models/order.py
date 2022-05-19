from flask import current_app as app
from app.models.cart import Cart
from flask_login import current_user

from .user import User
from .product import Product

class Order:
    def __init__(self, oid, product_id, buyer_id, seller_id, date, fulfilled, num_items):
        self.oid = oid
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.date = date
        self.fulfilled = fulfilled
        self.num_items = num_items

    @staticmethod
    #method to find seller, check their inventory against cart quantity, and modify databases
    def sellerInv(user_id):
        try:
            # rows = app.db.execute(
            #     """ SELECT * 
            #         FROM Sells AS s INNER JOIN 
            #         (SELECT * FROM HasInCart  
            #         WHERE user_id = :user_id) AS h
            #         ON s.pid = h.product_id
            #         GROUP BY seller_id, s.pid""", 
            #                                      user_id = user_id)

            order_id = app.db.execute(
                """ 
                    SELECT MAX(oid)+1 FROM Orders
                """
            )[0][0]

            print("ORDER ID", order_id)
            
            #finds sellers and their product inventory for each product in the cart
            options = app.db.execute(""" 
            SELECT sells.quantity, sells.pid, sells.seller_id, cart.quantity 
            FROM (
                SELECT *
                FROM HasInCart
                WHERE user_id = :user_id
                ) AS cart
                INNER JOIN Sells AS sells ON sells.pid = cart.product_id
                ORDER BY sells.quantity DESC
            """, 
                                user_id = user_id)

            print("HERE")

            #selecting every product in user's cart
            pids = app.db.execute(
                """SELECT product_id, quantity
                FROM HasInCart
                WHERE user_id = :uid
                """,
                uid = user_id
            )

            print("HERE2")

            #find total price of cart items
            productsCart = Cart.displayCart(user_id)
            print("HERE2.1")
            totalPrice = [p.price * p.quantity for p in productsCart]
            print("HERE2.2")
            priceList = []
            for p in productsCart:
                priceList.append(p.price * p.quantity)
            print("prices", priceList)
            productPrice = 0
            sumPrice = 0
            for x in totalPrice:
                sumPrice += x

            print("HERE3")

            #check if Balance is sufficient decrement accordingly
            if current_user.balance >= sumPrice:
                newBal = current_user.balance - sumPrice
                
                app.db.execute("""
                UPDATE Users 
                SET balance = :newBal
                WHERE uid = :user_id
                RETURNING uid""",
                                    newBal = newBal,
                                    user_id = user_id)
            else:
                return

            print("HGERE2.3")
            
            #finds the sellers for each product who hold the most inventory of that product
            sellers = []
            for pid, quant in pids:
                for option in options:
                    if option[1] == pid:
                        if quant <= option[0]:
                            
                            sellers.append(option[2])
                            newQuant = option[0] - quant

                            # run SQL to decrease quantity of this seller's inventory

                            app.db.execute(
                                """
                                UPDATE Sells
                                SET quantity = :newQuant
                                WHERE seller_id = :option
                                AND pid = :pid2
                                RETURNING pid
                                """,
                                            newQuant = newQuant,
                                            option = option[2],
                                            pid2 = option[1]
                            )
                            #calculate and add balance to seller

                            print("HHERE2.5")
                
                            
                            newSellBal = priceList[productPrice]
                            
                            app.db.execute("""
                                UPDATE Users
                                SET balance = balance + :seller_bal
                                WHERE uid = :seller_id
                                RETURNING uid""",
                                            seller_bal = newSellBal,
                                            seller_id = option[1])

                            print("HGERE3")

                            #add to order
                            Order.addToOrder(order_id, option[1], user_id, option[2], quant)

                            #delete item from Cart
                            app.db.execute(
                                """
                                DELETE FROM HasInCart 
                                WHERE user_id = :user_id
                                AND product_id = :pid2
                                RETURNING user_id
                                """,
                                            user_id = user_id,
                                            pid2 = option[1]
                                
                            )

                        else:
                            # no seller has enough
                            sellers.append(-1)
                            print("NOT ENOUGH")
                
                        break

        except Exception as e:
            print(e)

    @staticmethod
    def addToOrder(oid, product_id, user_id, seller_id, num_items):
        fulfilled = False
        try:
            rows = app.db.execute(""" INSERT INTO Orders(oid, product_id, user_id, seller_id, fulfilled, num_items)
            VALUES(:oid, :product_id, :user_id, :seller_id, :fulfilled, :num_items)""",
                                                                                            oid = oid,
                                                                                            product_id = product_id,
                                                                                            user_id = user_id,
                                                                                            seller_id = seller_id,
                                                                                            
                                                                                            fulfilled = fulfilled,
                                                                                            num_items = num_items)

        except Exception as e:
            print(e)

    @staticmethod
    def displayOrder(user_id):
        try:
            rows = app.db.execute(""" SELECT * FROM Orders WHERE user_id = :user_id ORDER BY date DESC""",
                                                                        user_id = user_id)

            orders = []   
            past_id = rows[0][0]
            running = []                                     
            for order in rows:
                if order[0] != past_id:
                    # ONE ORDER COMPLETE
                    orders.append(running)
                    running = []
                    past_id = order[0]

                running.append(order)

            if running:
                orders.append(running)

            return orders
        except Exception as e:
            print(e)
            return None

    def seller_orders(seller_id):
        seller_id = int(seller_id)
        rows = app.db.execute('''
        SELECT oid, product_id, user_id, seller_id, date, fulfilled, num_items
        FROM Orders
        WHERE seller_id = :seller_id
        ORDER BY date DESC
        ''',
                seller_id = seller_id)
## Make more intuitive so you can follow all the weird array stuff
## Use other class imports to make it easier
        q = []
        for order in rows:
            user_info = app.db.execute('''
            SELECT firstname, lastname, adrs, uid
            FROM Users
            WHERE uid = :user_id
            ''', user_id = order.user_id)[0]
            q.append(user_info)

        r = []
        for order in rows:
            product_info = app.db.execute('''
            SELECT name, price, image, description, category, creator_id
            FROM Products, Orders
            WHERE pid = :product_id
            ''', product_id = order.product_id, num_items = order.num_items)[0]
            r.append(product_info)

        return [(Order(*rows[j]), q[j], r[j]) for j in range(len(rows))]

    @staticmethod
    def fulfill(oid, pid):
        try:
            app.db.execute("""
            Update Orders
            Set fulfilled = True
            WHERE oid = :oid AND product_id = :pid
            """, 
                    oid=oid, pid = pid)
            return oid
        except Exception as e:
            print(e)
            return None
    
    @staticmethod
    def unfulfill(oid, pid):
        try:
            app.db.execute("""
            Update Orders
            Set fulfilled = False
            WHERE oid = :oid AND product_id = :pid
            """, 
                    oid=oid, pid = pid)
            return oid
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get(oid, pid):
        oid = int(oid)
        pid = int(pid)
        rows = app.db.execute("""
SELECT oid, product_id, user_id, seller_id, date, fulfilled, num_items
FROM Orders
WHERE oid = :oid AND product_id = :pid""",
                        oid=oid, pid=pid)
        return Order(*(rows[0])) if rows is not None else None

    @staticmethod
    def fulfilled(items):
        for item in items:
            if item.fulfilled == False:
                return False
        return True

    @staticmethod
    def totalPrice(oid):
        pids = app.db.execute("""
        SELECT product_id, num_items
        FROM Orders
        WHERE oid = :oid
        """, oid = oid)
        
        total = 0
        for pid, quant in pids:
            price = app.db.execute("""
        SELECT price
        FROM Products
        WHERE pid = :pid
        """, pid = pid)[0][0]
            total += price * quant

        return total
