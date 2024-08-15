from compmatrix import db


class App(db.Model):
    __tablename__ = 'app'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    company_url = db.Column(db.Text)
    release_date = db.Column(db.Date)
    genre_id = db.Column(db.Integer)
    artwork_large_url = db.Column(db.Text)
    seller_name = db.Column(db.Text)
    five_star_ratings = db.Column(db.Integer)
    four_star_ratings = db.Column(db.Integer)
    three_star_ratings = db.Column(db.Integer)
    two_star_ratings = db.Column(db.Integer)
    one_star_ratings = db.Column(db.Integer)

    sdks = db.relationship('AppSDK', back_populates='app', lazy='dynamic')


class SDK(db.Model):
    __tablename__ = 'sdk'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    slug = db.Column(db.Text)
    url = db.Column(db.Text)
    description = db.Column(db.Text)

    apps = db.relationship('AppSDK', back_populates='sdk', lazy='dynamic')


class AppSDK(db.Model):
    __tablename__ = 'app_sdk'
    __table_args__ = (
        db.PrimaryKeyConstraint('app_id', 'sdk_id'),
    )

    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), primary_key=True)
    sdk_id = db.Column(db.Integer, db.ForeignKey('sdk.id'), primary_key=True)
    installed = db.Column(db.Boolean)

    app = db.relationship('App', back_populates='sdks')
    sdk = db.relationship('SDK', back_populates='apps')
