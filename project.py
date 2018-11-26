# -------------------------------------------------------------------------
# Import Section
# -------------------------------------------------------------------------

from flask import (Flask, render_template, request,
                   redirect, jsonify, url_for, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import httplib2
import json
import random
import string
import requests
from functools import wraps

# -------------------------------------------------------------------------
# Flask framework initialization
# -------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = 'super_secret_key'

CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# -------------------------------------------------------------------------
# Connect to Database and create database session
# -------------------------------------------------------------------------

#engine = create_engine('sqlite:///catalog.db')
engine = create_engine(
        'postgresql+psycopg2://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# -------------------------------------------------------------------------
# Create anti-forgery state token
# -------------------------------------------------------------------------


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    if 'username' not in login_session:
        return render_template('login.html', STATE=state)
    else:
        flash("""
            User is already login. I you want to login through another
            account then click on the logout button.""")
        return redirect(url_for('showCatalog'))

# -------------------------------------------------------------------------
# Google authentication and authorization
# -------------------------------------------------------------------------


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """'"style = "width: 300px; height: 300px;
        border-radius:150px;-webkit-border-radius: 150px;
        -moz-border-radius: 150px;">'"""
    flash("You are now logged in as '%s'" % login_session['username'])
    print "done!"
    return output


# -------------------------------------------------------------------------
# User Helper Functions
# -------------------------------------------------------------------------


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# -------------------------------------------------------------------------
# DISCONNECT - Revoke a current user's token and reset their login_session
# -------------------------------------------------------------------------


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# -------------------------------------------------------------------------
# JSON endpoints to view public information
# -------------------------------------------------------------------------


@app.route('/catalog/JSON')
def catalogJson():
    """Return the JSON objects of all categories and items."""
    catergories = session.query(Categories).all()
    items = session.query(Items).all()
    return jsonify(
        Categories=[c.serialize for c in catergories],
        Items=[i.serialize for i in items]
    )


@app.route('/catalog/<int:categories_id>/JSON')
def catalogItemsJson(categories_id):
    """Return the JSON objects of items of specific category."""
    catergories = session.query(Categories).filter_by(id=categories_id).one()
    items = session.query(Items).filter_by(categories_id=catergories.id)
    return jsonify(Categories_Items=[i.serialize for i in items])


@app.route('/catalog/<int:categories_id>/<int:itemID>/JSON')
def itemJson(categories_id, itemID):
    """Return the JSON objects of specific item."""
    items = session.query(Items).filter_by(
        id=itemID, categories_id=categories_id)
    return jsonify(Item=[i.serialize for i in items])


# -------------------------------------------------------------------------
# Show all categories and latest Items.
# -------------------------------------------------------------------------

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Categories).order_by(asc(Categories.name))
    items = session.query(Items).order_by(Items.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template(
            'publiccatalog.html', categories=categories, items=items
        )
    else:
        return render_template(
            'usercatalog.html', categories=categories, items=items
        )


# -------------------------------------------------------------------------
# User Login check
# -------------------------------------------------------------------------


def login_required(f):
    #  @wraps, which will preserve information about the original function
    @wraps(f)
    # This will accept an arbitrary number of positional and keyword arguments
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x


# -------------------------------------------------------------------------
# Create a new item
# -------------------------------------------------------------------------


@app.route('/catalog/item/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    categories = session.query(Categories).all()
    if request.method == 'POST':
        newItem = Items(
            name=request.form['name'], description=request.form['description'],
            categories_id=request.form['categories_id'],
            user_id=login_session['user_id']
        )
        session.add(newItem)
        session.commit()
        flash('New "%s" Item Successfully Created' % (newItem.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html', categories=categories)


# -------------------------------------------------------------------------
# View specific Items of specify category
# -------------------------------------------------------------------------


@app.route('/catalog/<int:category_id>/items')
def catalogItems(category_id):
    categories = session.query(Categories).order_by(asc(Categories.name))
    category = session.query(Categories).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(categories_id=category.id)
    rows = session.query(Items).filter_by(categories_id=category.id).count()
    return render_template(
        'catalogItems.html', rows=rows, categories=categories,
        category=category, items=items
    )


# -------------------------------------------------------------------------
# Description of Item according to the user
# -------------------------------------------------------------------------


@app.route('/catalog/<int:category_id>/<int:itemId>/description')
def itemDescription(category_id, itemId):
    items = session.query(Items).filter_by(id=itemId).one()
    if 'username' not in login_session:
        return render_template('publicItemDescription.html', items=items)
    else:
        return render_template('userItemDescription.html', items=items)


# -------------------------------------------------------------------------
# Edit the item according to the user
# -------------------------------------------------------------------------


@app.route(
    '/catalog/<int:category_id>/<int:itemId>/edit', methods=['GET', 'POST']
)
@login_required
def editItem(category_id, itemId):
    editedItem = session.query(Items).filter_by(id=itemId).one()
    category = session.query(Categories).filter_by(id=category_id).one()
    categories = session.query(Categories).all()
    print login_session['user_id']
    print category.user_id

    if login_session['user_id'] != editedItem.user_id:
        flash("""
            You are not authorized to edit item to this category.
            Please create your own Item in order to edit
            them.""")
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['categories_id']:
            editedItem.course = request.form['categories_id']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'editItem.html', item=editedItem, categories=categories)


# -------------------------------------------------------------------------
# Delete the item according to the user
# -------------------------------------------------------------------------


@app.route(
    '/catalog/<int:category_id>/<int:itemId>/delete', methods=['GET', 'POST']
)
def deleteItem(category_id, itemId):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Items).filter_by(id=itemId).one()
    if login_session['user_id'] != itemToDelete.user_id:
        flash("""
            You are not authorized to delete item to this category.
            Please create your own Item in order to delete
            them.""")
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# -------------------------------------------------------------------------
# Disconnect based on provider
# -------------------------------------------------------------------------


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


# -------------------------------------------------------------------------
# Create the localhost with port number
# -------------------------------------------------------------------------


if __name__ == '__main__':
    app.run()
