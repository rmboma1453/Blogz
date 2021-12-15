from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120),unique=True)
    hash = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='owner')

    def __init__(self, email, hash):
        self.email = email
        self.hash = hash

    def __repr__(self):
        return '<User %r>' % self.email

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))    
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))   

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner


