
from ast import keyword
from crypt import methods
from math import ceil, floor
from random import *
from tokenize import single_quoted
import urllib.request, json

import os
from flask_app import app
from flask_app.models.user import User
from flask_app.models.joke import Joke
from flask_app.models.comment import Comment


from flask import render_template,redirect,request,session,flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def homepage():
    
    return render_template('index.html')

@app.route('/process', methods = ['POST'])
def process_user():
    if request.form['password']:
       
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
       
        data = {
            'fname': request.form['fname'],
            'lname': request.form['lname'],
            'email': request.form['email'],
            'password': request.form['password'],
            'c_password': request.form['c_password'],
            'phash': pw_hash
        }
        if not User.validate_user(data):
            return redirect("/")
        User.register_user(data)
        session['fname'] = request.form['fname']
        session['email'] = request.form['email']
        you = User.get_by_email(data)
        session['id'] = you.id
        return redirect(f"/success/{you.id}")
    else:
        data = {
            'fname': request.form['fname'],
            'lname': request.form['lname'],
            'email': request.form['email'],
            'password': request.form['password'],
            'c_password': request.form['c_password'],
            
        }
        if not User.validate_user(data):
            flash('please enter password')
            return redirect("/")
        
@app.route('/success')
def loggedout():
    jokes = Joke.viewrecentjokes()
    return render_template('success.html', jokes = jokes)
@app.route('/success/<int:id>')
def logged_in(id):
    if 'email' not in session:
        flash("Not logged in")
        return redirect('/success')
    data = {
        'email': session['email'],
        'id': id

    }
    jokes = Joke.viewrecentjokes()

    return render_template('success.html', name = session['fname'], id = id, jokes = jokes)
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/success")
@app.route('/login', methods=['post'])
def login():
    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data)
    
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        # if we get False after checking the password
        flash("Invalid Email/Password")
        return redirect("/")
    session['fname'] = user_in_db.first_name
    session['email'] =user_in_db.email
    id = user_in_db.id
    session['id'] = user_in_db.id
    return redirect(f"/success/{id}")

@app.route('/getjoke/')
def getjoke():
    apilength = Joke.lengthapi()
    userlength = Joke.lengthusers()
    if apilength+userlength != 0:
        ratio = apilength/(userlength+apilength)
    else:
        ratio = 1
    
    
    if random() < ratio:
        url = "https://v2.jokeapi.dev/joke/Any?safe-mode"

        response = urllib.request.urlopen(url)
        data = response.read()
        dict = json.loads(data)
        
        if dict['type'] == 'single':
            joke = dict['joke']
            index = 0
            for x in joke:
                index = index+1
                if x == '%':
                    joke = f"{joke[:index]}%{joke[index:]}"
                    index =index+1
                
            data = {
                
                'content': joke
            }
            if Joke.isUnique(data):
                Joke.insert_joke(data)
            ajoke = Joke.getone(data)
         
            if 'id' in session:
                id = session['id']
            if 'id' not in session:
                id = ''
            
        
            
            return redirect(f'/view/{ajoke.id}')
        if dict['type'] == 'twopart':
            joke = f"{dict['setup']} {dict['delivery']}"
            index = 0
            for x in joke:
                index = index+1
                if x == '%':
                    joke = f"{joke[:index]}%{joke[index:]}"
                    index =index+1
            data = {
                
                'content': joke
            }
            if Joke.isUnique(data):
                Joke.insert_joke(data)
            ajoke = Joke.getone(data)
           
            if 'id' in session:
                id = session['id']
            if 'id' not in session:
                id = ''
            data={
                'id': ajoke.id
            }
            
            return redirect(f'/view/{ajoke.id}')
    else:
        id = randint(2, userlength+1)
        data={
            'id': id
        }
        ajoke = Joke.getoneid(data)
       
        if 'id' in session:
            id = session['id']
        if 'id' not in session:
            id = ''
        data={
                'id': ajoke.id
            }
        
        redirect(f'/view/{ajoke.id}')
    return redirect(f'/success/{session["id"]}')

@app.route('/favorite/<int:id>')
def favorite_joke(id):
    if 'id' not in session:
        flash('Please login to favorite')
        return redirect(f'/view/{id}')
    data = {
        'user_id': session['id'],
        'joke_id': id
    }
    if  not Joke.favorite_exists(data):
        Joke.insert_favorite(data)
        return redirect(f'/view/{id}')
    else:
        flash('you have already favorited!')
        return redirect(f'/view/{id}')

@app.route('/view/<int:id>')
def viewbyid(id):
    data = {
        'id': id

    }
    joke = Joke.getoneid(data)

    userlist = User.getusersandcomments(data)
    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    if not userlist:
        return render_template('view.html',  joke = joke, ids = ids, jokeid = joke.id, userlist=[])
    return render_template('view.html',  joke = joke, ids = ids, jokeid = joke.id, userlist=userlist)

@app.route('/showfavorites/<int:id>')
def showallfaves(id):
    data = {
        'id': id
    }
    user = User.userfaves(data)
    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    
    return render_template('view_favorites.html',user = user, ids= ids)

@app.route('/delete/<int:id>')
def deletefave(id):
    data = {
        'user_id': session['id'],
        'joke_id': id
    }
    User.deletefaves(data)
    return redirect(f"/showoneuser/{session['id']}")

@app.route('/seeothers/<int:id>')
def getusersf(id):
    data = {
        'id': id
    }
    joke = Joke.usersfavorited(data)
    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    return render_template("viewjokeandusers.html", joke = joke, id = ids, jokeid= id)

@app.route('/viewpage/<int:pg>')
def viewall(pg):
    jokes = Joke.viewalljokes()
    newlist = []
    numpages = ceil(len(jokes)/50)

    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    if numpages == 0:
        return render_template("viewalljokes.html", jokes = newlist, numpages = numpages, ids=ids, pg=pg)
    if pg<1:
        
        return redirect('/viewpage/1')
    if pg>numpages:
        
        return redirect(f'/viewpage/{numpages}')
    for x in range(pg*50-50, pg*50):
        if not 0 <= x < len(jokes):
            break
        newlist.append(jokes[x])
    return render_template("viewalljokes.html", jokes = newlist, numpages = numpages, ids=ids, pg=pg)



@app.route('/create/<int:id>', methods= ['post'])
def submitjoke(id):

    if 'id' not in session:
        flash('Login to submit a joke')
        return redirect('/success')
    joke = request.form['content']
    if not Joke.validateform(joke):
        return redirect(f'/success/{session["id"]}')
    index = 0
    for x in joke:
        index = index+1
        if x == '%':
            joke = f"{joke[:index]}%{joke[index:]}"
            index =index+1
       
    data = {
        'user_id': id,
        'content': joke
    }
    joke = Joke.insert_ujoke(data)
    return redirect(f"/view/{joke.id}")

@app.route('/makecomment/<int:joke_id>', methods = ['post'])
def submitcomment(joke_id):
    if 'id' not in session:
        flash('Must login/register to comment!')
        return redirect(f'/view/{joke_id}')
    data ={
        'user_id': session['id'],
        'joke_id': joke_id,
        'content': request.form['content']
    }
    content = request.form['content']
    if Joke.validateform(content):
        Comment.insertcomment(data)
        return redirect(f'/view/{joke_id}')
    return redirect(f'/view/{joke_id}')
@app.route('/showoneuser/<int:id>')
def getauser(id):
    data = {
        'id': id
    }
    userf = User.userfaves(data)
    jokes = Joke.jokesubmitted(data)

    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    
    return render_template('showprofile.html', userf= userf, jokes = jokes, id = ids)
@app.route('/searchjokes', methods = ['post'])
def searchjokes():
    if request.form['search']:
        session['data'] = '%%'+request.form['search']+'%%'
        

        return redirect('/viewpagesearch/1')
@app.route('/viewpagesearch/<int:pg>')
def viewallsearc(pg):
    data = {
        'search': session['data']
    }
    jokes = Joke.searchforjokes(data)
    newlist = []
    numpages = ceil(len(jokes)/50)
   
    if pg<1:
        
        return redirect('/viewpage/1')
    if pg>numpages:
        
        return redirect(f'/viewpage/{numpages}')
    for x in range(pg*50-50, pg*50):
        if not 0 <= x < len(jokes):
            break
        newlist.append(jokes[x])
    if 'id' in session:
        ids = session['id']
    if 'id' not in session:
        ids = ''
    return render_template("viewalljokes.html", jokes = newlist, numpages = numpages, ids=ids, pg=pg)
@app.route('/deletejoke/<int:id>')
def deletejoke(id):
    data ={
        'id': id
    }
    
    Joke.deljoke(data)
    return redirect(f'/showoneuser/{session["id"]}')
