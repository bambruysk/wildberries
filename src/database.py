from peewee import *
import datetime

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django
class ProductModel(BaseModel):
    article = CharField(unique=True)
    brand = CharField()
    supplier = CharField()
    created = DateTimeField(default=datetime.datetime.now)
    price = DecimalField()
    goods_name = TextField() 
    
class OrderCountModel(BaseModel):
    product = ForeignKeyField(Product)
    order_count = IntegerField()
    timestamp = DateTimeField(default=datetime.datetime.now)




