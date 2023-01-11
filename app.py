from hack import app, create_db, db
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, UploadForm
from hack.models import User, CSVFile
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sklearn
import stripe

stripe.api_key = app.config['STRIPE_SECRET_KEY']

create_db(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists.'
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
    return render_template('reg.html', form=form, mess=mess)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found.'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password.'
    return render_template('login.html', mess=mess, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_csvs():
    form = UploadForm()
    mess = 'Please upload a CSV.'
    if form.validate_on_submit():
        file = form.csv.data
        filename_ = current_user.username + '.csv'
        file.save(os.path.join('hack/static/csvs/', filename_))
        new_csv = CSVFile(path=filename_, uploader=current_user.username)
        current_user.csvs.append(new_csv)
        current_user.sep = form.sep.data
        db.session.add(new_csv)
        db.session.add(current_user)
        db.session.commit()
        return  redirect(url_for('home'))
    return render_template('upload.html', form=form, mess=mess)

@app.route('/algorithms', methods=['GET', 'POST'])
@login_required
def algorithms():
    if len(current_user.csvs) <= 0:
        flash('Please upload a CSV first.')
    else:
        code=[]
        num_cols = []
        if current_user.membership != 'Free':
                data = pd.read_csv(f'hack/static/csvs/{current_user.username}.csv', sep=f'{current_user.sep}')
                for c in data.columns:
                    if data[c].dtypes != object:
                        num_cols.append(c)
                    if request.method == 'POST':
                        print(request.form.get('column_sel'))
                        code = ['import pandas as pd', 'import numpy as np', 'from sklearn.linear_model import LinearRegression', 'import sklearn']
                        predict = request.form.get('column_sel')
                        code.append(f"data = pd.load_csv('{request.form.get('csv_name')}.csv', sep='{current_user.sep}')")
                        code.append(f"predict = '{predict}'")
                        code.append('x = np.array(data.drop([predict], 1))')
                        code.append('y = np.array(data[predict])')
                        code.append('x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.1)')
                        code.append('model = LinearRegression()')
                        code.append('model.fit(x_train, y_train)')
                        code.append('accuracy = model.score(x_test, y_test)')
                        code.append('prediction = model.predict(x_test)')
        else:
            flash('You need to purchase FlaskML PRO to use this feature.', category='error')
            return redirect(url_for('home'))
    return render_template('algorithms.html', code=code, num_cols=num_cols)

@app.route('/upgrade', methods=['GET','POST'])
@login_required
def upgrade():
    if current_user.membership == 'Free':
        amount = 2499
            # customer = stripe.Customer.create(
            #     email=current_user.email,
            #     source=request.form['stripeToken']
            # )

            # stripe.Charge.create(
            #     customer=customer.id,
            #     amount=amount,
            #     currency='usd',
            #     description='Flask Charge'
            # )
        if request.method == 'POST':
            current_user.membership = 'PRO'
            db.session.add(current_user)
            db.session.commit()
        return render_template('upgrade.html', amount=amount, key=app.config['STRIPE_PUBLISHABLE_KEY'])
    return redirect(url_for('home'))

@app.route('/algorithms_knn', methods=['GET', 'POST'])
@login_required
def knn():
    if len(current_user.csvs) <= 0:
        flash('Please upload a CSV first.', 'error')
    else:
        code=[]
        num_columns = []
        if current_user.membership != 'Free':
                data = pd.read_csv(f'hack/static/csvs/{current_user.username}.csv', sep=request.form.get('csv_sep'))
                num_columns = []
                for c in data.columns:
                    if data[c].dtypes != object:
                        num_columns.append(c)
                if request.method == 'POST':
                    code = ['import pandas as pd', 'import numpy as np', 'from sklearn.neighbours import KNeighboursClassifier', 'import sklearn']
                    predict = request.form.get('column_sel')
                    code.append(f"data = pd.read_csv('{request.form.get('csv_name')}.csv', sep='{current_user.sep}')")
                    code.append(f"predict = {predict}")
                    code.append(f"x = np.array(data.drop([predict], 1))")
                    code.append(f"y = np.array(data[predict])")
                    code.append('x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.1)')
                    code.append(f"model = KNeighborsClassifier(n_neighbors={request.form.get('n_neighbours')})")
                    code.append('model.fit(x_train, y_train)')
                    code.append('accuracy = model.score(x_test, y_test)')
                    code.append('prediction = model.predict(x_test)')
        else:
            flash('You need to purchase FlaskML PRO to use this feature.')
    return render_template('algorithms_knn.html', code=code, num_cols=num_columns)
if __name__ == '__main__':
    app.run(debug=True)
