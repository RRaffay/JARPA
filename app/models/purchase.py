from flask import current_app as app

# Creates a class for the Orders Table
class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
# A function which returns a specific purchase based on its id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

# A function which returns all purchases by a specific person (uid) in descending order by date
    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT oid, user_id, product_id, date
FROM Orders
WHERE user_id = :uid
ORDER BY date DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

# AND date >= :since