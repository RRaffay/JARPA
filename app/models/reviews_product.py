from flask import current_app as app
from .user import User

#Create class for the Reviews_Product Table
class Reviews_Product:
    def __init__(self, rating, review, uid, pid, date):
        self.rating = rating
        self.review = review
        self.uid = uid
        self.pid = pid
        self.date = date

   #An ordering function which gets all values in the product review table done by a single user
   # in descending order 
    @staticmethod
    def get_reviews_product(uid):
        rows = app.db.execute('''
SELECT rating, review, user_id, product_id, date
FROM Reviews_Product
WHERE user_id = :uid
ORDER BY date DESC
''',
                              uid=uid)
        return [(Reviews_Product(*row)) for row in rows]
# An ordering function which gets all values in the seller review table done by a single user
# in descending order
    @staticmethod
    def get_reviews_seller(uid):
        rows = app.db.execute('''
SELECT rating, review, user_id, seller_id, date
FROM Reviews_Seller
WHERE user_id = :uid
ORDER BY date DESC
''',
                              uid=uid)
        return [(Reviews_Product(*row)) for row in rows]
    
   # Function for adding a product review to the database (used in later form) 
    @staticmethod
    def addProductReviewSQL(rating, review, uid, pid):
        try:
            rows = app.db.execute("""
INSERT INTO Reviews_Product(rating, review, user_id, product_id)
VALUES(:rating, :review, :uid, :pid)
RETURNING product_id
""",
                                  rating = rating,
                                  review = review  + ".",
                                  uid = uid,
                                  pid = pid,
                                  )
            return True
        except Exception as e:
            # Product Review could not be added
            print(e)
            return None

# Function for removing a product review from the product review database
    @staticmethod
    def removeProductReview(uid, pid):
        app.db.execute('''
DELETE FROM Reviews_Product
WHERE product_id = :pid 
AND user_id = :uid
RETURNING product_id
''',
                              pid=pid,
                              uid=uid)
        return True


# Function for updating a product review from the product review database
    @staticmethod
    def updateProductReview(rating, review, uid, pid):
        try:
            rows = app.db.execute("""
UPDATE Reviews_Product
SET rating = :rating, review = :review
WHERE product_id = :pid AND user_id = :uid
RETURNING product_id
""",
                                  rating = rating,
                                  review = review  + ".",
                                  uid = uid,
                                  pid = pid,
                                  )
            return True
        except Exception as e:
            # Product Review could not be updated
            print(e)
            return None

# Function for adding a review to the seller review database
    @staticmethod
    def addSellerReview(rating, review, uid, sid):
        try:
            rows = app.db.execute("""
INSERT INTO Reviews_Seller(rating, review, user_id, seller_id)
VALUES(:rating, :review, :uid, :sid)
RETURNING seller_id
""",
                                  rating = rating,
                                  review = review  + ".",
                                  uid = uid,
                                  sid = sid,
                                  )
            return True
        except Exception as e:
            # Seller Review could not be added
            print(e)
            return None

# Function for removing a review from the seller review database
    @staticmethod
    def removeSellerReview(uid, sid):
        app.db.execute('''
DELETE FROM Reviews_Seller
WHERE seller_id = :sid 
AND user_id = :uid
RETURNING seller_id
''',
                              sid=sid,
                              uid=uid)
        return True


# Funciton for updating a review from the seller review database
    @staticmethod
    def updateSellerReview(rating, review, uid, sid):
        try:
            rows = app.db.execute("""
UPDATE Reviews_Seller
SET rating = :rating, review = :review
WHERE seller_id = :sid AND user_id = :uid
RETURNING seller_id
""",
                                  rating = rating,
                                  review = review  + ".",
                                  uid = uid,
                                  sid = sid
                                  )
            return True
        except Exception as e:
            # Seller Review could not be updated
            print(e)
            return None