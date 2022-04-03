from operator import truediv
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Joke:
    dbname = 'jokes'
    def __init__(self, data):
        self.id = data['id']
        self.content = data['content']
        self.users = []
        self.user = {}
    @classmethod
    def isUnique(cls, data):
        query = 'SELECT * FROM jokes WHERE content = %(content)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        if len(result)>0:
            return False
        return True
    @classmethod
    def insert_joke(cls, data):
        query = 'INSERT INTO jokes (content, user_id) VALUES ( %(content)s, 1);'
        connectToMySQL(cls.dbname).query_db(query, data)
    @classmethod
    def insert_ujoke(cls, data):
        query = 'INSERT INTO jokes (content, user_id) VALUES ( %(content)s, %(user_id)s);'
        connectToMySQL(cls.dbname).query_db(query, data)
        query = 'SELECT * FROM jokes WHERE content = %(content)s && user_id =%(user_id)s;'
        resutl = connectToMySQL(cls.dbname).query_db(query, data)
        return cls(resutl[0])

    @classmethod
    def getone(cls, data):
        query = 'SELECT * FROM jokes WHERE content = %(content)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        print(result)
        return cls(result[0])
    @classmethod
    def getoneid(cls, data):
        query = 'SELECT * FROM jokes JOIN users ON jokes.user_id =users.id WHERE jokes.id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        print(result)
        joke = cls(result[0])
        user_data = {
        "id" : result[0]['users.id'],
        "first_name" : result[0]['first_name'],
        "last_name" : result[0]['last_name'],
        "email" : result[0]['email'],
        "password" : result[0]['password']
        }
        userr = user.User(user_data)
        joke.user = userr
        return joke

        return cls(result[0])
    @classmethod
    def insert_favorite(cls,data):
        query = 'INSERT INTO favorites (user_id, joke_id) VALUES ( %(user_id)s, %(joke_id)s);'
        connectToMySQL(cls.dbname).query_db(query, data)
        flash('Saved to favorites!')
    @classmethod
    def favorite_exists(cls,data):
        query = 'SELECT * FROM favorites WHERE user_id = %(user_id)s && joke_id = %(joke_id)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        print(result)
        if len(result)<1:
            return False
        else:
            return True
    @classmethod
    def usersfavorited(cls,data):
        query = 'SELECT * FROM jokes JOIN favorites on favorites.joke_id = jokes.id LEFT JOIN users on favorites.user_id = users.id WHERE jokes.id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        print(result)
        if len(result) == 0:
            return False
        joke = cls(result[0])
        for row in result:
            user_data={
                'id': row['favorites.user_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'password': row['password']
            }
            joke.users.append(user.User(user_data))
        return joke
    @classmethod
    def viewalljokes(cls):
        query = 'SELECT * from jokes'
        result = connectToMySQL(cls.dbname).query_db(query)
        jokes = []
        for row in result:
            joke_data={
                'id': row['id'],
                'content': row['content']
            }
            jokes.append(cls(joke_data))
        return jokes
    @classmethod
    def viewrecentjokes(cls):
        query = 'SELECT * FROM jokes ORDER BY id DESC LIMIT 50'
        result = connectToMySQL(cls.dbname).query_db(query)
        jokes = []
        for row in result:
            joke_data={
                'id': row['id'],
                'content': row['content']
            }
            jokes.append(cls(joke_data))
        return jokes
    @classmethod
    def lengthapi(cls):
        query = 'SELECT * from jokes where user_id = 1'
        result = connectToMySQL(cls.dbname).query_db(query)
        return len(result)
    @classmethod
    def lengthusers(cls):
        query = 'SELECT * from jokes where not user_id = 1'
        result = connectToMySQL(cls.dbname).query_db(query)
        return len(result)
    @classmethod
    def jokesubmitted(cls,data):
        query = 'SELECT * from jokes JOIN users on jokes.user_id = users.id where user_id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query,data)
        
        jokes = []
        for row in result:
            joke_data={
                'id': row['id'],
                'content': row['content']
            }
            jokes.append(cls(joke_data))
        return jokes
    @classmethod
    def searchforjokes(cls, data):
        query = 'SELECT * FROM jokes WHERE content like %(search)s'
        result = connectToMySQL(cls.dbname).query_db(query,data)
        
        jokes = []
        for row in result:
            joke_data={
                'id': row['id'],
                'content': row['content']
            }
            jokes.append(cls(joke_data))
        print(jokes)
        return jokes
    @classmethod
    def deljoke(cls,data):
        query = 'DELETE from favorites where joke_id = %(id)s'
        connectToMySQL(cls.dbname).query_db(query,data)
        query = 'DELETE from comments where joke_id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query,data)
        query = 'DELETE from jokes where id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query,data)
    @staticmethod
    def validateform(data):
        print(data)
        print(len(data))
        if len(data)<3:
            flash('Submission must be 3 characters or more')
            return False
        else:
            return True

            


        