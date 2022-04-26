from flask import Flask, jsonify
from sqlalchemy import create_engine
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
import click
import pandas as pd
import decimal, datetime
import json
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'YE"2^y3^%6Y9}x8P'
app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy (app)
def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Data(db.Model):
    productId =   db.Column(db.Integer, primary_key=True)
    name =      db.Column(db.String(700), nullable=False, default=None)
    descShort =  db.Column(db.String(1200),  default=None)
    descLong =    db.Column(db.String(1200), default=None)
    visible =         db.Column(db.Integer, default=1)
    stock =    db.Column(db.Integer, default=1)
    price =           db.Column(db.Integer,  default=0)
    categories = db.Column(db.String(2500), default=None)
    image =   db.Column(db.String(2500), default=None)
    featuredProduct = db.Column(db.Integer, default=0)

    def __init__(self, productId, name, descShort, descLong, visible, stock, price, categories, image, featuredProduct):
        self.productId = productId
        self.name = name
        self.descShort = descShort
        self.descLong = descLong
        self.visible = visible
        self.stock = stock
        self.price = price
        self.categories = categories
        self.image = image
        self.featuredProject = featuredProduct

    def __repr__(self):
        return    {"productId": self.productId,
            "name": self.name,
            "descShort": self.descShort,
            "descLong": self.descLong,
            "visible": self.visible,
            "stock": self.stock,
            "price": self.price,
            "categories": self.categories,
            "image": self.image,
            "featuredProject": self.featuredProduct}
        

@app.cli.command("load-data")
@click.argument("fname")
def load_data(fname):
    print ('*** Load from file: ' + fname)

    df = pd.read_csv( fname )

    for row in df.itertuples(index=False):
        print ('***************************')

        v_productId = row[0]
        v_name = row[1]
        v_descShort = row[2]
        v_descLong = row[3]
        v_visible = row[4]
        v_stock = row[5]
        v_price = row[6]
        v_categories = row[7]
        v_image = row[8]
        v_featuredProject = row[9]

        print ( 'Product    = ' + str( v_productId             ) )
        print ( 'Product    = ' + str( v_name             ) )
        print ( 'descShort  = ' + str( v_descShort        ) )
        print ( 'descLong   = ' + str( v_descLong         ) )
        print ( 'Visible    = ' + str( v_visible          ) )
        print ( 'Stock      = ' + str( v_stock            ) )
        print ( 'Price      = $' + str( v_price           ) )
        print ( 'Categories = ' + str( v_categories       ) )
        print ( 'ImageURL   = ' + str( v_image            ) )
        print ( 'Featured   = ' + str( v_featuredProject  ) )
        # def __init__(self, productId, name, descShort, descLong, visible, stock, price, categories, image, featuredProduct):
        obj = Data(v_productId, v_name, v_descShort, v_descLong, v_visible,  v_stock, v_price, v_categories, v_image, v_featuredProject)
        db.session.add ( obj )
    
    #should had looped through all rows in dataframe !
    db.session.commit()

# Default Route 
@app.route('/')
@cross_origin() # allow all origins all methods.
def hello_world():
    retVal  = 'Hello, the database has ('+str( len(Data.query.all()) )+') rows' 
    retVal += '<br /> See loaded <a href="/data">data</a>.'

    return retVal

# Data Route - Shows the loaded information
@app.route('/data')
@cross_origin() # allow all origins all methods.
def data():

    retVal = 'Rows = ' + str( len(Data.query.all()) ) + '<br />' 

    for row in Data.query.all():
        retVal += '<br />' + str( row.__repr__() )             
    return retVal

# Data Route - Shows the JSON data 
@app.route('/products')
@cross_origin() # allow all origins all methods.
def results():
    retVal = []
    for row in Data.query.all():
        print(row.productId)
        retVal.append({'productId': row.productId,'name': row.name, 'descShort': row.descShort, 'descLong': row.descLong, 'visible': row.visible, 'stock': row.stock,'price': row.price,'categories': row.categories,'image': row.image })
    return jsonify(retVal), {'content-type':'application/json'}

@app.route('/products/<paramid>')
@cross_origin() # allow all origins all methods.
def resultIs(paramid):

    product_query = Data.query.filter(Data.productId == paramid).one_or_none()
    if product_query is None:
        abort(
            404,
            "Person not found for Id",
        )
    queryObj = {'productId': product_query.productId,'name': product_query.name, 'descShort': product_query.descShort, 'descLong': product_query.descLong, 'visible': product_query.visible, 'stock': product_query.stock,'price': product_query.price,'categories': product_query.categories,'image': product_query.image }
    return jsonify(queryObj), {'content-type':'application/json'}



