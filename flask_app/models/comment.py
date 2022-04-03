
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Comment:
    dbname = 'jokes'
    def __init__(self, data):
        self.id = data['id']
        self.content = data['content']
        self.user_id = data['user_id']
        self.joke_id = data['joke_id']
    @classmethod
    def insertcomment(cls,data):
        query = "INSERT INTO comments (user_id, joke_id, content) VALUES (%(user_id)s,%(joke_id)s,%(content)s)"
        result = connectToMySQL(cls.dbname).query_db(query,data)
