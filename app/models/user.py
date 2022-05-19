from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, adrs, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.adrs = adrs
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT *
FROM Users
WHERE email = :email
""",
                              email=email)
        print("GET BY AUTH", rows)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][2], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][:2] + rows[0][3:]))

#     @staticmethod
#     def get_password(email):
#         rows = app.db.execute("""
# SELECT password
# FROM Users
# WHERE email = :email
# """,
#                               email=email)
#         if not rows:  # email not found
#             return None
#         else:
#             return rows[0][0]

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def email_exists_not_uid(email, uid):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email AND NOT uid = :uid
""",
                              email=email,
                              uid =uid)
        return len(rows) > 0

    @staticmethod
    def all_users():
        rows = app.db.execute("""
SELECT *
FROM Users
""")
        return rows

    @staticmethod
    def register(email, password, firstname, lastname, adrs):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, adrs, balance)
VALUES(:email, :password, :firstname, :lastname, :adrs, :balance)
RETURNING uid
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname,
                                  adrs=adrs,
                                  balance=0.0)
            uid = rows[0][0]
            return User.get(uid)
        except Exception as e:
            # likely email already in use; better error checking and
            # reporting needed
            print(e)
            return None

    @staticmethod
    def update(uid, email, password, firstname, lastname, adrs, passChanged):

        if passChanged:
            try:
                app.db.execute("""
    UPDATE Users
    SET email = :email, firstname = :firstname, lastname = :lastname, adrs = :adrs, password = :password
    WHERE uid = :uid
    RETURNING uid
    """,
                                    uid=uid,
                                    email=email,
                                    firstname=firstname,
                                    lastname=lastname,
                                    adrs=adrs,
                                    password=generate_password_hash(password))
                return id
            except Exception as e:
                # likely email already in use; better error checking and
                # reporting needed
                print(e)
                return None
        else:
            try:
                app.db.execute("""
    UPDATE Users
    SET email = :email, firstname = :firstname, lastname = :lastname, adrs = :adrs
    WHERE uid = :uid
    RETURNING uid
    """,
                                    uid=uid,
                                    email=email,
                                    firstname=firstname,
                                    lastname=lastname,
                                    adrs=adrs)
                return id
            except Exception as e:
                # likely email already in use; better error checking and
                # reporting needed
                print(e)
                return None

    @staticmethod
    def updateBalance(uid, balance):
        print("UPDATE BALANCE", uid, balance)
        try:
            app.db.execute("""
UPDATE Users
SET balance = :balance
WHERE uid = :uid
RETURNING uid
""",
                                  uid=uid,
                                  balance=balance)
            return id
            
        except Exception as e:
            print(e)
            return None

    @staticmethod
    @login.user_loader
    def get(uid):
        rows = app.db.execute("""
SELECT uid, email, firstname, lastname, adrs, balance
FROM Users
WHERE uid = :uid
""",
                              uid=uid)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def is_seller(uid):
        rows = app.db.execute("""
SELECT *
FROM Sells
WHERE seller_id = :uid
""",
                              uid=uid)

        print("IS SELLER", rows)
        return len(rows) > 0

    @staticmethod
    def is_creator(uid):
        rows = app.db.execute("""
    SELECT *
    FROM Products
    WHERE creator_id = :uid    
    """,
                                uid=uid)

        print("IS CREATOR", rows)
        return len(rows) > 0

    @staticmethod
    def ratings(uid):
        reviews = app.db.execute("""
SELECT rating, review, user_id
FROM Reviews_Seller
WHERE seller_id = :uid
ORDER BY rating DESC
""",
                              uid=uid)

        for i in range(len(reviews)):
            reviews[i] = list(reviews[i]) + [User.get_name(reviews[i][2])]

        return reviews

    @staticmethod
    def get_name(uid):
            name = app.db.execute("""
    SELECT firstname, lastname
    FROM Users
    WHERE uid = :uid
""",
                            uid=uid)
            return name[0][0] + " " + name[0][1]