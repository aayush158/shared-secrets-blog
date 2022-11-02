from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import math
from datetime import datetime
from models import Contact , Posts
app = Flask(__name__)

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server=True

app.secret_key = 'super-secret-key'
#if(local_server):app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']else:

app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)




@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    #[0:params['no_of_posts']]
    #posts = posts[]
    page = request.args.get('page')
    if (not str(page).isnumeric()) :
        page = 1
    page = int(page)
    posts = posts[(page-1) * int(params['no_of_posts']) : (page-1) * int(params['no_of_posts']) + int(params['no_of_posts'])]

    if (page==1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif (page==last) :
        prev = "/?page=" + str(page - 1)
        next = "#"
    else :
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def edit(sno) :
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST' :
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno=='0':
                post = Posts(title=box_title, slug=slug, content=content, subtitle=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else :
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.subtitle = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if ('user' in session and session['user'] == params['admin_user']) :
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts = posts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params[ 'admin_user' ] and userpass == params[ 'admin_password' ]) :
            posts = Posts.query.all()
            session['user'] = username
            return render_template('dashboard.html', params=params, posts = posts)

    return render_template('login.html', params=params)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/contact", methods=["GET", "POST"])

def contact():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        '''db.session.add(entry)
        db.session.commit()'''


    return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


app.run(debug=True)
