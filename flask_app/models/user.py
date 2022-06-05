

from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import joke
from flask_app.models import comment

from flask import flash
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    dbname = 'jokes'
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.jokes = []
        self.comments = {}
        
    @classmethod
    def register_user(cls, data):
        query = 'INSERT INTO Users (first_name, last_name, email, password) VALUES ( %(fname)s, %(lname)s, %(email)s, %(phash)s );'
        connectToMySQL(cls.dbname).query_db(query, data)
        
    @classmethod
    def get_by_email(cls, data):
        query = 'SELECT * FROM Users WHERE email = %(email)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        if len(result)<1:
            return False
        return cls(result[0])
    @classmethod
    def get_everbody_else(cls, data):
        query = 'SELECT * FROM users WHERE NOT email = %(email)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        return result
    @classmethod
    def email_exists(cls, data):
        query = 'SELECT * FROM Users WHERE email = %(email)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
        if len(result)>0:
            return False
        return True
    @classmethod
    def userfaves(cls,data):
        query = 'SELECT * FROM users LEFT JOIN favorites on favorites.user_id = users.id LEFT JOIN jokes on favorites.joke_id = jokes.id WHERE users.id = %(id)s'
        result = connectToMySQL(cls.dbname).query_db(query, data)
    
        user = cls(result[0])
        if len(result) == 0:
            return False
        if result[0]['joke_id'] == None:
            return user
        
        for row in result:
            jokes_data={
                'id': row['joke_id'],
                'content': row['content']
            }
            user.jokes.append(joke.Joke(jokes_data))
        
        return user
    @classmethod
    def deletefaves(cls,data):
        query = 'Delete FROM favorites WHERE user_id = %(user_id)s && joke_id =%(joke_id)s'
        connectToMySQL(cls.dbname).query_db(query, data)
    @classmethod
    def getusersandcomments(cls,data):
        query = 'SELECT * FROM comments JOIN users on users.id = comments.user_id WHERE joke_id = %(id)s '
        result = connectToMySQL(cls.dbname).query_db(query, data)
  
        if len(result) == 0:
            return []
        if result[0]['content'] == None:
            return []
        userlist = []
        for row in result:
            user_data ={
                'id': row['users.id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'password': row['password']

            }
            auser = User(user_data)
            comment_data={
                'id': row['id'],
                'content': row['content'],
                'user_id': row['user_id'],
                'joke_id': row['joke_id']
            }

            acomment = comment.Comment(comment_data)
            auser.comments = acomment
            userlist.append(auser)
    
        return userlist

    
    @staticmethod
    def validate_user(data):
        is_valid = True
        if len(data['fname']) < 3:
            flash("First name must be at least 3 characters")
            is_valid = False
        if len(data['lname']) < 3:
            is_valid = False
            flash("Last name must be at least 3 characters")
        if len(data['password']) < 8:
            is_valid = False
            flash("Password must be at least 8 characters")
        if not data['password'] == data['c_password']:
            is_valid = False
            flash("Please confirm passwords match")
        if not EMAIL_REGEX.match(data['email']): 
            flash("Invalid email address!")
            is_valid = False
        if not User.email_exists(data):
            flash('email already taken')
            is_valid = False
        
        
        return is_valid