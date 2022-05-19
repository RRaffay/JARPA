from flask import current_app as app

# A class created for the Seller Table in the DB
class Seller:
    def __init__(self, seller_id,pid,quantity):
        self.pid = pid
        self.seller_id = seller_id
        self.quantity = quantity

# Fucntion which returns sellers that sell a speciifc product (pid)
    @staticmethod
    def get_seller_by_pid(pid):
        rows = app.db.execute('''
SELECT seller_id, pid,quantity
FROM Sells
WHERE pid = :pid
ORDER BY quantity DESC
''', pid=pid)
        return [Seller(*row) for row in rows]
        
"""
    @staticmethod
    def get_inventory(seller_id):
        rows = app.db.execute('''
SELECT Products.name, Products.price, Product.description, Products.image, Seller.quantity 
FROM Seller, Products        
WHERE Sells.seller_id = :seller_id AND Products.pid = Sells.pid
        ''', seller_id = seller_id)
        return 
"""