from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from messenger import Messenger
from functools import wraps
from forms import Item
import os
#messenger 
message = Messenger()



app = Flask(__name__)

#bootstrap
Bootstrap5(app)

#confing variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///portfolio.db')

#Flask-login
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#admin-only decorator 
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        try:
            current_user.id == 1
        except Exception:     
            return abort(403)
        else:
            if current_user.id !=1:
                return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

#database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class PortfolioItem(db.Model):
    __tablename__ ="items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique= True)
    img: Mapped[str] = mapped_column(String, nullable= False)
    url: Mapped[str] = mapped_column(String, nullable = False)
    type: Mapped[str] = mapped_column(String, nullable=False)

    
class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique= True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    def get_id(self):
        return str(self.id)


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET","POST"])
def home():
    print(current_user)  
    result = db.session.execute(db.select(PortfolioItem))
    portfolio_items = result.scalars().all()
    
    if request.method == "POST":
        data = request.form
        Messenger().send_message(name =data['name'], email=data['email'], subject= data['subject'], message = data['message'])
        msg_sent = True
    else:
        msg_sent = False
    try:
        current_user.id 
    except AttributeError: 
        edit = False
    else:
        edit = True
    
    return render_template('index.html', msg_sent = msg_sent, portfolio_items= portfolio_items, edit = edit)

@app.route('/delete<int:id>', methods= ['POST', "GET"])
@admin_only
def delete_item(id):  
    requested_item = db.get_or_404(PortfolioItem, id)
    db.session.delete(requested_item)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add_portfolio_item', methods=["GET","POST"])
@admin_only
def add_portfolio_item():
    form = Item()
    try:
        request.args['item_added']
    except KeyError:
        item_added = False

    if form.validate_on_submit():
      new_item= PortfolioItem(
        title = form.title.data,
        img = form.img.data,
        url = form.url.data,
        type = form.type.data
      )  
      db.session.add(new_item)
      db.session.commit()
      return redirect(url_for('add_portfolio_item', item_added = True))
    return render_template('add_item.html', form = form, item_added = item_added)

@app.route('/login/<string:name>/<string:password>', methods=["GET", "POST"])
def login(name, password):
    result = db.session.execute(db.select(User).where(User.name == name))
    user = result.scalar()
    if not user:
        return "Try again"
    elif not check_password_hash(user.password, password):
        return 'try one more time'
    else:
        login_user(user)
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register/<string:name>/<string:password>')
def register(name, password):
    hash_and_salted_password = generate_password_hash(password,
    method='pbkdf2:sha256',
    salt_length=8)
    new_user = User(
        name= name, 
        password = hash_and_salted_password
    )
    db.session.add(new_user)
    db.session.commit()
    result = db.session.execute(db.select(User).where(User.name == name))
    user = result.scalar()
    login_user(user)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug= True)