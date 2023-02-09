from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy


# Create a new Flask app instance / object
app = Flask(__name__)

# config db connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# initialize db
db = SQLAlchemy(app)


class Contact(db.Model):
    # Define the primary key column "id" as an integer
    id = db.Column(db.Integer, primary_key=True)
    # Define the name column as a string of maximum length 200, which cannot be null
    name = db.Column(db.String(200), nullable=False)
    # Define the phone column as a string of maximum length 200, which cannot be null
    phone = db.Column(db.String(200), nullable=False)
    # Define the email column as a string of maximum length 200, which cannot be null
    email: object = db.Column(db.String(200), nullable=False)
    # Define the date_created column as a DateTime, with default value set to the current timestamp
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    # Define the string representation of a Contact object

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'date_created': self.date_created
        }

    def __repr__(self):
        # Return a string that includes the id of the Contact object
        return '<Contact %r>' % self.id


# routes
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        contact_name = request.form['name']
        contact_phone = request.form['phone']
        contact_email = request.form['email']
        new_contact = Contact(name=contact_name, phone=contact_phone, email=contact_email)
        try:
            db.session.add(new_contact)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your contact'
    else:
        contacts = Contact.query.order_by(Contact.date_created).all()
        return render_template('index.html', contacts=contacts)


@app.route('/delete/<int:id>')
def delete(id):
    # query db for contact with id
    contact_to_delete = Contact.query.get_or_404(id)
    # try / except error handling
    try:
        # delete contact from db & commit changes
        db.session.delete(contact_to_delete)
        db.session.commit()
        # reload homepage & refresh contacts list
        return redirect('/')
    except:
        return 'There was a problem deleting that contact'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        contact.name = request.form['name']
        contact.phone = request.form['phone']
        contact.email = request.form['email']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your contact'
    else:
        return render_template('update.html', contact=contact)


@app.route('/view/<int:id>')
def view(id):
    contact = Contact.query.get_or_404(id)
    return render_template('view.html', contact=contact)


@app.route('/api/contacts')
def api_contacts():
  # return db query results as a JSON list
  return jsonify([contact.serialize for contact in Contact.query.all()])


@app.post('/api/contacts')
def add_contact():
    data = request.get_json()
    try:
        contact = Contact(name=data['name'], email=data['email'], phone=data['phone'])
        db.session.add(contact)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        return app.response_class(response={"status": "failure"},
                                  status=500,
                                  mimetype='application/json')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
