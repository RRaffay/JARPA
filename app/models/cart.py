from types import CodeType
from flask import current_app as app


class Cart:
    def __init__(self, id, uid, pid, discount):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.discount = discount
        
    #have function to check if user_id and product_id is NULL
    #if NULL, call addCart
    #if not NULL, call updateQuantity

    @staticmethod
    def checkQuantity(user_id, quantity, product_id):
        try:
            rows = app.db.execute(""" SELECT * FROM HasInCart 
            WHERE user_id = :user_id AND product_id = :product_id""",
                                                    user_id = user_id,
                                                    quantity = quantity,
                                                    product_id = product_id)
            print(rows)
            if rows:
                Cart.updateQuantity(user_id, quantity, product_id)
            else:
                Cart.addCart(user_id, quantity, product_id)

        except Exception as e:
            print(e)


    @staticmethod
    def updateQuantity(user_id, quantity, product_id):
        try:
            rows = app.db.execute(""" UPDATE HasInCart 
                                      SET quantity = quantity + 1
                                      WHERE user_id = :user_id 
                                      AND product_id = :product_id """,
                                                        user_id = user_id,
                                                        quantity = quantity,
                                                        product_id = product_id)

        except Exception as e:
            print(e)

    @staticmethod
    def applyCoupon(id, coupon):
        if coupon:
            try:
                print(coupon)
                discount = app.db.execute(""" SELECT discount FROM Coupons WHERE code = :code""", code = coupon)[0][0]
                
                print("DISCOINT", discount)

                if discount:
                    app.db.execute(""" UPDATE HasInCart 
                                        SET discount = :discount
                                        WHERE user_id = :id
                                        RETURNING user_id """,
                                                    id = id,
                                                    discount = discount)

            except Exception as e:
                print(e)

    @staticmethod
    def addCart(user_id, quantity, product_id):
        try:
            #print(user_id, quantity, product_id)
            rows = app.db.execute(""" INSERT INTO HasInCart(user_id, quantity, product_id)
                VALUES(:user_id, :quantity, :product_id)""", 
                                                    user_id = user_id,
                                                    quantity = quantity,
                                                    product_id = product_id)
        except Exception as e:
            # Product could not be added to Cart
            print(e)
        

    @staticmethod
    def displayCart(user_id):
        rows = app.db.execute(""" SELECT name, description, price * 1-discount AS price, p.pid, c.user_id, c.product_id, c.quantity
                                FROM Products AS p
                                INNER JOIN HasInCart AS c ON c.product_id = p.pid 
                                WHERE c.user_id = :user_id
                                ORDER BY name asc
                                """,
                                                        user_id = user_id
                                                        )
        
        return rows

    #method to update cart quantity
    @staticmethod
    def updateQuantity(user_id, quantity, product_id):
        try:
            rows = app.db.execute(""" 
            UPDATE HasInCart
            SET quantity = :quantity
            WHERE user_id = :user_id
            AND product_id = :product_id
            """, 
                        user_id=user_id,
                        quantity=quantity,
                        product_id=product_id)
            
        except Exception as e:
            print(e)
        
    
    #method to delete line item from Cart
    @staticmethod
    def deleteCart(user_id, product_id):
        try:
            rows = app.db.execute("""
            DELETE FROM HasInCart 
            WHERE user_id = :user_id
            AND product_id = :product_id""",
            user_id=user_id,
            product_id=product_id)
        except Exception as e:
            print(e)