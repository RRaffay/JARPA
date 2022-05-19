from flask import current_app as app

# Class for the category database of a product
class Category:
    def __init__(self,name):
        self.name = name

# Simple function for getting all avaliable categories in the database
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Categories
''')
        return [Category(*row) for row in rows]
