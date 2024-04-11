from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
import uuid
from flask import Flask, render_template, request, redirect, jsonify
import plotly.graph_objs as go
import plotly.offline as pyo
from collections import Counter
import json, datetime
import statistics as stats
import os, requests
from flask import Flask, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID
from flask_cors import CORS
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker




app = Flask(__name__)
app.app_context().push()

try:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:8000/ticktock'
    print("connection secured")
except psycopg2.Error as e:
    print(e)


CORS(app)
db = SQLAlchemy()
db.init_app(app)

class User_details(db.Model):
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    # Add more fields as needed
    
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user_details.user_id'), unique=True)
    phone_number = db.Column(db.String(20))
    
    def __init__(self, user_id, phone_number):
        self.user_id = user_id
        self.phone_number = phone_number     

class customer_watches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user_details.user_id', ondelete='CASCADE'), nullable=False)
    brand=db.Column(db.String(100))
    modelNumber= db.Column(db.String(100))
    series=db.Column(db.String(100))
    year=db.Column(db.Integer)
    box=db.Column(db.Boolean, default=False, nullable=False)
    price=db.Column(db.Float, default=0.0)
    soldPrice = db.Column(db.Float, default=0.0)
    deleted = db.Column(db.Boolean, default=False)
    owned=db.Column(db.Boolean, default=True)
    
    
    def __init__(self, user_id, brand, modelNumber, series, year, box, price, sold_price, deleted):
        self.user_id = user_id
        self.brand=brand     
        self.modelNumber=modelNumber
        self.series=series
        self.year=year
        self.box=box
        self.price=price
        self.sold_price= sold_price
        self.deleted= deleted

class Nodes(db.Model):
    node_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    created_at=db.Column(db.DateTime())
    brand = db.Column(db.String(100), primary_key=True, nullable=False)
    name = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Float, default=0.0)

    def __init__(self, created_at, brand, name):
        self.created_at=created_at
        self.brand = brand
        self.name = name 
        # self.price = price
    # Define any other columns specific to the nodes table

class Markets(db.Model):
    market_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    created_at=db.Column(db.DateTime())
    node_id = db.Column(db.Integer,  nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    seriesGroup = db.Column(db.String(100),primary_key=True, nullable=False)
    name = db.Column(db.String(100),nullable=False)
    series = db.Column(db.String(100),primary_key=True, nullable=False)
    seriesUrl = db.Column(db.String(250))
    price = db.Column(db.Float, default=0.0)

    # Define the composite foreign key referencing the Instrument table's composite primary key
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['node_id', 'brand'],
            ['nodes.node_id', 'nodes.brand']
        ),
    )
    

    def __init__(self, created_at, node_id, brand,seriesGroup,series, name,seriesUrl):
        self.created_at=created_at
        self.node_id = node_id
        self.brand = brand
        self.seriesGroup = seriesGroup
        self.series = series
        self.name = name
        self.seriesUrl = seriesUrl
        # self.price = price
 
    # Define any other columns specific to the markets table
class Instruments(db.Model):
    instrument_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at=db.Column(db.DateTime())
    modelNumber = db.Column(db.String(100),primary_key=True, nullable=False)
    name = db.Column(db.String(100),nullable=False)
    market_id = db.Column(db.Integer, nullable=False)
    seriesGroup = db.Column(db.String(100),  nullable=False)
    series = db.Column(db.String(100), nullable=False)
    modelUrl = db.Column(db.String(250))
    year = db.Column(db.Integer)
    price = db.Column(db.Float, default=0.0)
    # Define the composite foreign key referencing the Market table's composite primary key
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['market_id', 'seriesGroup', 'series'],
            ['markets.market_id', 'markets.seriesGroup', 'markets.series']
        ),
    )

    def __init__(self, created_at, modelNumber,name, market_id,seriesGroup,series,modelUrl, year):
        self.created_at=created_at
        self.modelNumber = modelNumber
        self.name = name
        self.market_id = market_id
        self.seriesGroup = seriesGroup
        self.series = series
        self.modelUrl = modelUrl
        self.year = year
        # self.price = price
    # Define any other columns specific to the markets table

class Watches(db.Model):
    watch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stockId = db.Column(db.String(150),primary_key=True, nullable=False)
    modelNumber = db.Column(db.String(100),  nullable=False)
    instrument_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(250))
    url = db.Column(db.String(100))
    date = db.Column(db.DateTime())
    dateString = db.Column(db.String(150))
    box = db.Column(db.Boolean, default=False, nullable=False)
    papers = db.Column(db.Boolean, default=False, nullable=False) 
    material = db.Column(db.String(150))
    strap = db.Column(db.String(150))
    itemTypeDescription = db.Column(db.String(100))
    limitedEdition = db.Column(db.Boolean, default=False, nullable=False)
    dial = db.Column(db.String(100))
    caseSize = db.Column(db.Integer)
    price = db.Column(db.Float)
    discountMargin = db.Column(db.Float)
    isComingSoon = db.Column(db.Boolean, default=False, nullable=False)
    isDiscounted = db.Column(db.Boolean, default=False, nullable=False)
    isSold = db.Column(db.Boolean, default=False, nullable=False)
    isPublished = db.Column(db.Boolean, default=False, nullable=False)
    isPriceOnApplication = db.Column(db.Boolean, default=False, nullable=False)
    isCurrentlyPresale = db.Column(db.Boolean, default=False, nullable=False)
    isCartierPartnership = db.Column(db.Boolean, default=False, nullable=False)

    # Define the composite foreign key referencing the Instrument table's composite primary key
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['modelNumber', 'instrument_id'],
            ['instruments.modelNumber', 'instruments.instrument_id']
        ),
    )


    def __init__(self, modelNumber,instrument_id, stockId, image, url,box,papers,limitedEdition, date,    dateString, material, strap, itemTypeDescription, dial, caseSize,
                    price,discountMargin, isComingSoon, isDiscounted, isSold, isPublished, isPriceOnApplication, 
                    isCurrentlyPresale, isCartierPartnership):

        self.stockId = stockId
        self.modelNumber = modelNumber
        self.instrument_id = instrument_id
        self.image = image
        self.url = url
        self.box = box
        self.papers = papers
        self.limitedEdition = limitedEdition
        self.date = date
        self.dateString = dateString
        self.material = material
        self.strap = strap
        self.itemTypeDescription = itemTypeDescription
        self.dial = dial
        self.caseSize = caseSize
        self.price = price
        self.discountMargin = discountMargin
        self.isComingSoon = isComingSoon
        self.isDiscounted = isDiscounted
        self.isSold = isSold
        self.isPublished = isPublished
        self.isPriceOnApplication = isPriceOnApplication
        self.isCurrentlyPresale = isCurrentlyPresale
        self.isCartierPartnership = isCartierPartnership  

    
db.create_all()

# # Event listener for Instrument model
# @event.listens_for(Instruments, 'after_insert')
# @event.listens_for(Instruments, 'after_update')
# def update_market_price(mapper, connection, target):
#     market_id = target.market_id
#     total_price = db.session.query(db.func.sum(Instruments.price)).filter_by(market_id=market_id).scalar()
#     # market = db.session.query(Markets).get(market_id)
#     market = db.session.get(Markets, (target.market_id, target.seriesGroup, target.series))
#     market.price = total_price or 0.0
#     db.session.commit()

# # # Event listener for Market model
# # @event.listens_for(Markets, 'after_insert')
# @event.listens_for(Markets, 'after_update')
# def update_node_price(mapper, connection, target):
#     brand = target.brand
#     total_price = db.session.query(db.func.sum(Markets.price)).filter_by(brand=brand).scalar()
#     # node = db.session.query(Nodes).filter_by(brand=target.brand).first()
#     node =db.session.query(Nodes).get((target.node_id, target.brand))
#     if node:
#         node.price = total_price or 0.0
#         db.session.commit()
# # Event listener for Watch model
# @event.listens_for(Watches, 'after_insert')
# @event.listens_for(Watches, 'after_update')
# def update_instrument_price(mapper, connection, target):
    
#     instrument_id = target.instrument_id
#     modelNumber = target.modelNumber
#     average_price = db.session.query(db.func.avg(Watches.price)).filter_by(instrument_id=instrument_id).scalar()
#     print("in watches ",instrument_id, modelNumber)
#     instrument = db.session.get(Instruments, (instrument_id, modelNumber))
#     # instrument = db.session.query(Instruments).get((instrument_id, modelNumber))
#     print("after geting form instruments ",instrument.price, average_price)
#     instrument.price = average_price or 0.0
#     print(instrument.price)
#     db.session.commit()
    # subsequently updating n market
    # print("before geting from markets ",instrument.market_id, instrument.series, instrument.seriesGroup)
    # market = db.session.get(Markets, (instrument.market_id, instrument.seriesGroup, instrument.series))
    # # market =db.session.query(Markets).get((instrument.market_id, instrument.series, instrument.seriesGroup))
    # total_market_price = db.session.query(db.func.sum(Instruments.price)).filter_by(market_id=instrument.market_id).scalar()
    # print("after getting market",total_market_price, market )
    # market.price = total_market_price
    # print(market.price, market.brand)
    # # db.session.commit()
    # # subsequently updating n node
    # print("before geting from node ",market.node_id, market.brand)
    # node =db.session.query(Nodes).get((market.node_id, market.brand))
    # total_node_price = db.session.query(db.func.sum(Markets.price)).filter_by(node_id=market.node_id).scalar()
    # print("after getting node",total_node_price, node.name)
    # node.price = total_node_price
    # print(node.price)
    # db.session.commit()


class WatchData:
    def __init__(self, nodes, markets, instruments, watches):
        # Access data from Node model

        self.brand = nodes.brand
        self.seriesGroup = markets.seriesGroup
        self.series = markets.series

        # Access data from Market model
        self.modelNumber = instruments.modelNumber
        self.modelUrl = instruments.modelUrl
        self.seriesUrl = markets.seriesUrl  
        self.limitedEdition = watches.limitedEdition
        self.box = watches.box
        self.papers = watches.papers
        self.year = instruments.year

        # Access data from Instrument model
        self.stockId = watches.stockId
        self.image = watches.image
        self.url = watches.url
        self.date = watches.date
        self.dateString = watches.dateString
        self.material = watches.material
        self.strap = watches.strap
        self.itemTypeDescription = watches.itemTypeDescription
        self.dial = watches.dial
        self.caseSize = watches.caseSize
        self.price = watches.price
        self.discountMargin = watches.discountMargin
        self.isComingSoon = watches.isComingSoon
        self.isDiscounted = watches.isDiscounted
        self.isSold = watches.isSold
        self.isPublished = watches.isPublished
        self.isPriceOnApplication = watches.isPriceOnApplication
        self.isCurrentlyPresale = watches.isCurrentlyPresale
        self.isCartierPartnership = watches.isCartierPartnership

# Query all watch data from the three tables using a join
result = db.session.query(Nodes, Markets, Instruments, Watches).\
    join(Markets, Nodes.brand == Markets.brand).\
    join(Instruments, Markets.series == Instruments.series).\
    join(Watches, Instruments.modelNumber == Watches.modelNumber).\
    all()

# Create a list of JoinedWatchData objects
all_watches = [WatchData(node, market, instrument, watch) for node, market, instrument, watch, in result]

# Query all watch data from the three tables using a join
# watches = db.session.query(Node, Market, Instrument).\
# join(Market, Node.id == Market.node_id).\
# join(Instrument, Market.id == Instrument.market_id).\
# all()
# # Create a list of data objects
# all_watches = []

# for node, market, instrument in watches:
#     print(node, market,instrument)
#     watch_data =  Watch(node, market, instrument)
#     print("watch_data ",watch_data)
   
#     all_watches.append(watch_data)
#     print(watch_data.dateString)
# print(all_watches)
# Serializing json  
# all_watches = json.dumps(all_watches, indent = 4) 
# print(all_watches)



def convert_to_bool_year(value):
       if value.lower() == 'yes':
            return True
       elif value.lower() == 'no':
            return False
       else:
            try:
                return int(value)
            except ValueError:
            # Try to extract the year from the string (e.g., 'Approx. 2013' -> 2013)
                year_str = value.split()[-1]
            try:
                return int(year_str)
            except ValueError:
                raise ValueError(f"Invalid boolean or integer value: {value}") 

def convert_to_bool(value):
    if value.lower() == 'yes':
        return True
    elif value.lower() == 'no':
        return False
    else:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid boolean value: {value}");

   

# @app.route('/create_db')
# def index():
#     file_path = 'watchfinder_all_watches_2023-05-23.json'

#     with open(file_path, 'r') as json_file:
#         data = json.load(json_file)

#     for item in data:
#         node = Node(brand=item['brand'], seriesGroup=item['seriesGroup'], series=item['series'])
#         db.session.add(node)
#         db.session.commit()

#         market = Market(node_id=node.id, modelNumber=item['modelNumber'], box=convert_to_bool(item['box']),
#                         papers=convert_to_bool(item['papers']), limitedEdition=convert_to_bool(item['limitedEdition']),
#                         year=convert_to_bool_year(item['year']))
#         db.session.add(market)
#         db.session.commit()

#         dateString = file_path.split('_')[3].split('.')[0]
#         isCartier = False
#         if 'isCartierPartnership' in item.keys():
#             isCartier = item['isCartierPartnership']
#         n = dateString.split('-')
#         date = datetime.datetime(int(n[0]), int(n[1]), int(n[2]))

#         instrument = Instrument(market_id=market.id, stockId=item['stockId'], image=item['image'],
#                                 url=item['url'],
#                                 date = date,
#                                 dateString= dateString,
#                                 material=item['material'], strap=item['strap'],
#                                 itemTypeDescription=item['itemTypeDescription'], dial=item['dial'],
#                                 caseSize=item['caseSize'], price=item['price'],
#                                 discountMargin=item['discountMargin'],
#                                 isComingSoon=item['isComingSoon'],
#                                 isDiscounted=item['isDiscounted'],
#                                 isSold=item['isSold'],
#                                 isPublished=item['isPublished'],
#                                 isPriceOnApplication=item['isPriceOnApplication'],
#                                 isCurrentlyPresale=item['isCurrentlyInPresale'],
#                                 isCartierPartnership=isCartier)

#         db.session.add(instrument)
#         db.session.commit()

#     return "<p>Index</p>"

       
# app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticks.sqlite3'




def serializeWatch(data):
    watch_item = {'stockId':data.stockId, 'image':data.image,'brand':data.brand,'series':data.series,'url':data.url,'date':data.date,
                  'dateString':data.dateString,'modelNumber':data.modelNumber,'box':data.box,'papers':data.papers,
                  'limitedEdition':data.limitedEdition,'year':data.year,'material':data.material, 'strap':data.strap, 'itemTypeDescription':data.itemTypeDescription,'dial':data.dial,
                  'caseSize':data.caseSize,'price':data.price,'discountingMargin':data.discountMargin,'isComingSoon':data.isComingSoon,
                  'isDiscounted':data.isDiscounted,'isSold':data.isSold, 'isPublished':data.isPublished, 
                  'isPriceOnApplication':data.isPriceOnApplication,'isCurrentlyPresale':data.isCurrentlyPresale,'isisCartierPartnership':data.isCartierPartnership}
    return watch_item
trace = go.Scatter(x=[1], y=[1,1.5,1.7])
data = [trace]
layout = go.Layout(
    title='My Graph',
    xaxis=dict(title='X Axis Label'),
    yaxis=dict(title='Y Axis Label'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig = go.Figure(data=data, layout=layout)
plot = pyo.plot(fig, output_type='div')

watch_dict = {'preload_count': 0, 'file_list': [], 'image_list':{}, 'logInfo':''}
processed_jsondata = {}
single_watch_dict = {}
# preloads some information after every 10 requests



def preload():
    print('preloading')
    processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
    if processedfile not in os.listdir(os.getcwd()):
        f = open(os.path.join(os.getcwd(),processedfile), 'w')
        
        with open(os.path.join(os.getcwd(), processedfile), 'w') as json_file:
            sorted_data = fetch_sorted_data()
            chart = {'total_market_cap_chart': watch_dict['total_market_cap_chart']} 
            performer_data = fetch_performers()
            # return
            indices_data = fetch_indices()
            processed_jsondata= {"data":sorted_data, "price_data":watch_dict['chart_data'], "watch_dict":watch_dict,
                                "market_cap_data":watch_dict['market_cap_data'], "chart":chart,
                                "performer_data": performer_data,"indices_data": indices_data
                                }
            json.dump(processed_jsondata, json_file)      
            print('Saved Preloaded Data')
    else:
        tmp_watchData = {}
        try: 
            with open(os.path.join(os.getcwd(), processedfile),'r') as json_file:
                processed_jsondata = json.load(json_file) 
                tmp_watchData = processed_jsondata['watch_dict']
                for key, value in tmp_watchData.items():
                    watch_dict[key] = value
                print('Obtained Preloaded Data', processed_jsondata.keys())   
        except:
            f = open(os.path.join(os.getcwd(),processedfile), 'w')
            with open(os.path.join(os.getcwd(), processedfile), 'w') as json_file:
                sorted_data = fetch_sorted_data()
                chart = {'total_market_cap_chart': watch_dict['total_market_cap_chart']} 
                performer_data = fetch_performers()
                # return
                indices_data = fetch_indices()
                processed_jsondata= {"data":sorted_data, "price_data":watch_dict['chart_data'], "watch_dict":watch_dict,
                                    "market_cap_data":watch_dict['market_cap_data'], "chart":chart,
                                    "performer_data": performer_data,"indices_data": indices_data
                                    }
                json.dump(processed_jsondata, json_file)      
                print('Saved Preloaded Data')            
    
def fetch_sorted_data():
    data = fetch_data()
    new_list = process_all_data(data)  
    return new_list

def fetch_performers():
    d = {}
    new_d = []
    for item in watch_dict['filtered_list']:
        d.setdefault(item['modelNumber'], {'dates':{}, 'image':item['image'], 'brand':item['brand'], 'stockId':item['stockId']})
        if item['dateString'] in d[item['modelNumber']]["dates"].keys():
            if int(item['price']) > 0:
                d[item['modelNumber']]["dates"][item['dateString']]['prices'].append(int(item['price']))
                d[item['modelNumber']]["dates"][item['dateString']]['avg'] = sum(d[item['modelNumber']]["dates"][item['dateString']]['prices'])/len(d[item['modelNumber']]["dates"][item['dateString']]['prices'])
        else:
            d[item['modelNumber']]["dates"][item['dateString']] = {'prices':[int(item['price'])], 'avg': int(item['price']),}
    # print(d)

    # print('fetch performers', len(watch_dict['filtered_list']))
    
    for mod, values in d.items():
        date_array = list(values["dates"].keys())
        date_array.sort()
        final_data = 0
        start_avg = 0
        end_avg = 0
        try:
            # final_data = values["dates"][date_array[-1]] 
            # data['date_list'][-7:] #
            if  watch_dict['date_list'][-7:][0] in date_array:
                start_avg = values["dates"][watch_dict['date_list'][-7:][0]]['avg'] 
            if date_array[-1] in watch_dict['date_list'][-7:]:
                end_avg = values["dates"][date_array[-1]]['avg'] 

            pre_val = (end_avg - start_avg)/start_avg*100
            val = str((end_avg - start_avg)/start_avg*100)
            m_val = f"{val.split('.')[0]}.{val.split('.')[1][:2]}"         

        except Exception as E:
            pre_val = 0
            val = str(0)
            m_val = 0
        change = m_val
        changecolor = None
        neg = True
        if pre_val > 0.1:
            neg = False           
        new_d.append({"model": mod,"image":values['image'], 'stockId':values['stockId'],'brand': values['brand'], 'change':change, 'negative': neg, 'start': start_avg, 'end':end_avg, 'start_date': watch_dict['date_list'][-7:][0], 'end_date':date_array[-1]})
    
    top_bad_performers = {}
    top_good_performers = {}
    for item in new_d:
        if item['negative']:
            top_bad_performers[float(item['change'])] = new_d.index(item)
        else:
            top_good_performers[float(item['change'])] = new_d.index(item)
    sorted_top_bad_performances = list(top_bad_performers.keys())
    sorted_top_bad_performances.sort()
    sorted_top_bad_performances = sorted_top_bad_performances[:10]

    sorted_top_good_performances = list(top_good_performers.keys())
    sorted_top_good_performances.sort(reverse=True)
    sorted_top_good_performances = sorted_top_good_performances[:10]
    # print(sorted_top_bad_performances)
    # print(sorted_top_good_performances)    

    bad_performance_models = []
    good_performance_models = []

    for change in sorted_top_bad_performances:
        bad_performance_models.append(new_d[top_bad_performers[change]])
    for change  in sorted_top_good_performances:
        good_performance_models.append(new_d[top_good_performers[change]])        

    watch_dict["positive_performance_models"] = good_performance_models
    watch_dict["negative_performance_models"] = bad_performance_models
    return {"positive_performance_models":good_performance_models, "negative_performance_models":bad_performance_models}
    
    
def fetch_indices():
    d = {}
    
    top_prices = {}
    bn_top_prices = {}
    price_per_brand = {} # for overall total
    price_per_bn = {}
    sorted_dir_list = os.listdir(os.path.join(os.getcwd(), 'allwatches'))
    sorted_dir_list.sort()
    count = {}
    
    for item in sorted_dir_list:  #gets a list of all the files in the folder
        with open(os.path.join(os.getcwd(), 'allwatches', item),'r') as f: #opens all files within the loop
            data = f.read()     
            counter = 0
            countem = 2
            a_list = json.loads(data)  
            filtered_list = []
            for watch_item in a_list:                 # data is looped through
                watch_item.pop('timestamp')           # the timestamp data has to be removed at it was the only parameter that made duplicate data differnt and undetectable
                date = item.split('_')[3].split('.')[0]
                bnKey = f"{watch_item['brand']}-{watch_item['series']}"
                if watch_item['brand'] not in list(price_per_brand.keys()):
                    price_per_brand[watch_item['brand']] = {date:{'price':[watch_item['price']],'count': 0}}
                if bnKey not in list(price_per_bn.keys()):
                    price_per_bn[bnKey] = {date:{'price':[watch_item['price']],'count': 0}}                    
                if date not in top_prices.keys():
                    top_prices[date] = []
                if date not in bn_top_prices.keys():
                    bn_top_prices[date] = []                    
                if date not in price_per_brand[watch_item['brand']].keys():
                    price_per_brand[watch_item['brand']][date] = {'price':[watch_item['price']],'count': 1}
                if date not in price_per_bn[bnKey].keys():
                    price_per_bn[bnKey][date] = {'price':[watch_item['price']],'count': 1}                    
                if watch_item not in filtered_list:   # confirms there is no duplicate
                    countem += 1
                    price_per_brand[watch_item['brand']][date]['price'].append(int(watch_item['price']))
                    price_per_brand[watch_item['brand']][date]['count'] = price_per_brand[watch_item['brand']][date]['count'] + 1
                    top_prices[date].append(int(watch_item['price']))


                    price_per_bn[bnKey][date]['price'].append(int(watch_item['price']))
                    price_per_bn[bnKey][date]['count'] =  price_per_bn[bnKey][date]['count'] + 1
                    bn_top_prices[date].append(int(watch_item['price']))
                    counter += 1
                    filtered_list.append(watch_item)  # appends the item if it doesnt exist in the list
                # else:

            count[date] = counter
    print('indices fetch in progress ....')
    import pprint
    new_price_per_brand = price_per_brand
    for brand, info in price_per_brand.items():
        for date, prices in info.items():
            sorted_prices = prices['price']
            sorted_prices.sort(reverse=True)
            if len(sorted_prices) > 30:
                new_price_per_brand[brand][date]['price'] = sum(sorted_prices[:30])/30
                new_price_per_brand[brand][date]['count'] = 30
            else:
                new_price_per_brand[brand][date]['price'] = sum(sorted_prices)/prices['count']


    new_price_per_bn = price_per_bn
    for bn, info in price_per_bn.items():
        for date, prices in info.items():
            sorted_prices = prices['price']
            sorted_prices.sort(reverse=True)
            if len(sorted_prices) > 30:
                new_price_per_bn[bn][date]['price'] = sum(sorted_prices[:30])/30
                new_price_per_bn[bn][date]['count'] = 30
            else:
                new_price_per_bn[bn][date]['price'] = sum(sorted_prices)/prices['count']

    # pprint.pprint(new_price_per_brand)
    new_top_prices = {}
    for items in top_prices.items():
        new_Data = items[1]
        new_Data.sort(reverse=True)
        new_top_prices[items[0]] = sum(new_Data[:100])/100


    new_bn_top_prices = {}
    for items in bn_top_prices.items():
        new_Data = items[1]
        new_Data.sort(reverse=True)
        new_bn_top_prices[items[0]] = sum(new_Data[:100])/100
        
    # pprint.pprint(new_top_prices)
    watch_dict['overall_market_index'] = new_top_prices
    watch_dict['brand_market_index'] = new_price_per_brand
    watch_dict['brand_name_market_index'] = new_price_per_bn
    print('indices fetch complete ....')
    return {'overall_market_index': new_top_prices, 'brand_market_index': new_price_per_brand, 'brand_name_market_index':new_price_per_bn}

def fetch_data(): # function to preload some watch data
    d = {}
    duplicated = 0
    filtered_list = []
    day_price_total = {}
    day_price_total_chart = {'labels':[], 'values':[]}
    # date_list = []
    datelist  = []

   
    # all_watches = Watch.query.all()
    # print(all_watches)
     
    for item in all_watches:
        # print(item)
        if item.dateString not in datelist:
            datelist.append(item.dateString)
        if item.dateString in day_price_total.keys():
            day_price_total[item.dateString] = day_price_total[item.dateString] + item.price
        else:
            day_price_total[item.dateString] = 0
    for item in sorted(day_price_total.keys()):
        day_price_total_chart['labels'].append(item)
        day_price_total_chart['values'].append(day_price_total[item])       

    start = datetime.datetime.now() - datetime.timedelta(days=8)
    end = datetime.datetime.now()  - datetime.timedelta(days=1)
    # d_watches = watch.query.filter(watch.date <= end).filter(watch.date >= start).all()
    d_watches = all_watches
    # d_watches = Watch.query.all()


    for item in d_watches:
        dated = serializeWatch(item)
        dated['date'] = str(dated['date'])
        filtered_list.append(dated)
    
    for item in filtered_list:                  # helps to generate the chart data i.e. prices
        d.setdefault(str(item['modelNumber']), [])   
        d[str(item['modelNumber'])].append(int(item['price']))   # adds all the prices for a model
    
    # print(datelist)
    duplid = 0
    dateArray  = list(datelist)
    dateArray.sort(reverse=True)

    b4yesterday = makeDate(dateArray[0]) - datetime.timedelta(days=2)
    yesterday = makeDate(dateArray[0]) - datetime.timedelta(days=1)
    today = makeDate(dateArray[0])

    # today_all_watches = Watch.query.filter(Watch.date <= today).filter(Watch.date >= yesterday).all()
    # yesterday_all_watches = Watch.query.filter(Watch.date <= yesterday).filter(Watch.date >= b4yesterday).all()
    today_all_watches = [watch for watch in all_watches if yesterday <= watch.date <= today]
    yesterday_all_watches = [watch for watch in all_watches if b4yesterday <= watch.date <= yesterday]        

    m = os.listdir(os.path.join(os.getcwd(), 'allwatches')) # tries to get the latest file
    m.sort()

    # print(dateArray)
    latest_file = dateArray[0]
    penultimate_file = dateArray[1]

    latest_file_filtered_list = []
    for data in today_all_watches:                 # data is looped through
        # item = serializeWatch(data)
        dated = serializeWatch(data)
        dated['date'] = str(dated['date'])
        if item not in latest_file_filtered_list:   # confirms there is no duplicate
            latest_file_filtered_list.append(dated)  # dappends the item if it doesnt exist in the list
        else:
            duplid += 1
    # date_list.sort()
    market_cap_diff = (day_price_total[latest_file] - day_price_total[penultimate_file])/ day_price_total[penultimate_file] * 100
    new_val = str(market_cap_diff)
    m_val = f"{new_val.split('.')[0]}.{new_val.split('.')[1][:2]}"
    market_cap_data = {'total_market_cap': day_price_total[latest_file], 'total_market_cap_yesterday':day_price_total[penultimate_file], 'market_cap_diff': market_cap_diff }

    if market_cap_diff > 0:
        market_cap_data['capcolor'] = 'text-green-500'
        market_cap_data['market_cap_diff'] = f"+{m_val}"
    else:
        market_cap_data['capcolor'] = 'text-red-500'
        market_cap_data['market_cap_diff'] = f"{m_val}"

    watch_dict['market_cap_data'] = market_cap_data
    watch_dict['total_market_cap'] = day_price_total[latest_file]
    watch_dict['total_market_cap_yesterday'] = day_price_total[penultimate_file]
    watch_dict['chart_data'] = d
    watch_dict['total_market_cap_chart'] = day_price_total_chart
    watch_dict['total_market_cap'] = day_price_total[latest_file]
    watch_dict['filtered_list'] = filtered_list
    watch_dict['latest_file_filtered_list'] = latest_file_filtered_list
    dateArray.sort()    
    watch_dict['date_list'] = dateArray


    return {'chart_data':d, 'date_list': dateArray, 'total_market_cap_chart':day_price_total_chart,
            'total_market_cap':day_price_total[latest_file],
            'total_market_cap_yesterday':day_price_total[penultimate_file], 
            'filtered_list':filtered_list, 'latest_file_filtered_list': latest_file_filtered_list,
            'market_cap_data':market_cap_data
            }  


def process_all_data(data):
    d = {}
    latest_d = {}
    for item in data['filtered_list']:
        d.setdefault(item['modelNumber'], {"prices": [], "years": [], "names": [], "brand": [], "dateString":'', "image":'','stockId':'', 'dates':{}})
        d[item['modelNumber']]["prices"].append(int(item['price']))
        d[item['modelNumber']]["years"].append(item['year'])
        d[item['modelNumber']]["brand"].append(item['brand'])
        d[item['modelNumber']]["names"].append(item['series'])
        d[item['modelNumber']]["dateString"] =item['dateString']
        d[item['modelNumber']]["image"] = item['image']
        d[item['modelNumber']]["stockId"] = item['stockId']

        if item['dateString'] in d[item['modelNumber']]["dates"].keys():
            if int(item['price']) > 0:
                d[item['modelNumber']]["dates"][item['dateString']]['prices'].append(int(item['price']))
                d[item['modelNumber']]["dates"][item['dateString']]['avg'] = sum(d[item['modelNumber']]["dates"][item['dateString']]['prices'])/len(d[item['modelNumber']]["dates"][item['dateString']]['prices'])
                d[item['modelNumber']]["dates"][item['dateString']]['max'] = min(d[item['modelNumber']]["dates"][item['dateString']]['prices'])
                d[item['modelNumber']]["dates"][item['dateString']]['max'] = max(d[item['modelNumber']]["dates"][item['dateString']]['prices'])
                d[item['modelNumber']]["dates"][item['dateString']]['sum'] = sum(d[item['modelNumber']]["dates"][item['dateString']]['prices'])

        else:
            d[item['modelNumber']]["dates"][item['dateString']] = {'prices':[int(item['price'])], 'avg': int(item['price']), 'min': int(item['price']), 'max': int(item['price'])}


    # m = [d[item] for item in list(d.keys())[:1]]
    # print(m)
    # import pprint
    # pprint.pprint(m)
    all_count = 0
    good_count = 0
    bad_count = 0   
    un_avail_count = 0 
    # print('datelist',data['date_list'])

    for mod, values in d.items():
        all_count += 1
        if all_count:
            mean_price = stats.mean(values["prices"])
            date_array = list(values["dates"].keys()) #list(values["dates"].keys())
            
            date_array.sort()
            final_data = 0
            start_avg = 0
            end_avg = 0
            circulating_supply = 0
            marketing_liquidity = 0
            start_avg_30 = 0
            end_avg_30 = 0


            try:
                
                # print('date_arrrrrt',date_array[-1])
                if date_array[-1] in data['date_list'][-7:]:  
                    final_data = values["dates"][date_array[-1]]
                    circulating_supply = len(list(final_data["prices"]))
                    marketing_liquidity = int_sum(list(final_data["prices"]))    
                    end_avg = values["dates"][date_array[-1]]['avg']                      

                if  data['date_list'][-7:][0] in date_array:
                    start_avg = values["dates"][data['date_list'][-7:][0]]['avg']         

                pre_val = (end_avg - start_avg)/start_avg*100
                val = str((end_avg - start_avg)/start_avg*100)
                m_val = f"{val.split('.')[0]}.{val.split('.')[1][:2]}"   
                
                
            except Exception as E:
                # print('error', str(E))
                
                pre_val = 0
                val = str(0)
                m_val = 0   

            try:
                if date_array[-1] in data['date_list'][-30:]:  
                    end_avg_30 = values["dates"][date_array[-1]]['avg']  
                if  data['date_list'][-30:][0] in date_array:
                    start_avg_30 = values["dates"][data['date_list'][-30:][0]]['avg']   
                else:
                    print(data['date_list'][-30:][0], date_array)
                    start_avg_30 = values["dates"][date_array[0]]['avg']   


                pre_val_30 = (end_avg_30 - start_avg_30)/start_avg_30*100
                val_30 = str((end_avg_30 - start_avg_30)/start_avg_30*100)
                m_val_30 = f"{val_30.split('.')[0]}.{val_30.split('.')[1][:2]}"     
                good_count += 1
            except Exception as E:
                print(start_avg_30, end_avg_30)
                print(str(E))
                bad_count += 1
                pre_val_30 = 0
                val_30 = str(0)
                m_val_30 = 0  
                  
            change = m_val
            changecolor = None
            change_30 = m_val_30
            changecolor_30 = None

            if pre_val > 0.1:
                changecolor = 'text-green-500'
                change = f"+{m_val}"

            else:
                changecolor = 'text-red-500'

            if pre_val_30 > 0.1:
                changecolor_30 = 'text-green-500'
                change_30 = f"+{m_val_30}"

            else:
                changecolor_30 = 'text-red-500'
            
            most_common_year = Counter(values["years"]).most_common(1)[0][0]
            try:
                if 'Approx' in most_common_year:
                    most_common_year = most_common_year.replace('Approx. ', '')      
            except:
                pass

            most_common_name = Counter(values["names"]).most_common(1)[0][0]
            most_common_brand = Counter(values["brand"]).most_common(1)[0][0]
            labelData = []
            pointData = []
            if circulating_supply < 2:
                for dat in values["dates"].items():
                    if dat[0] in data['date_list'][-7:]:
                        labelData.append('')
                        if dat[1]['avg']:
                            pointData.append(dat[1]['avg'])
                        else:
                            pointData.append(0)
            else:
                notIn = True
                for dat in values["dates"].items():
                    if dat[0] in data['date_list'][-7:]:
                        notIn  = False
                        if dat[1]['avg'] > 0:
                            labelData.append('')
                            pointData.append(dat[1]['avg'])
                if notIn:
                    for dat in values["dates"].items():
                        labelData.append('')
                        pointData.append(dat[1]['avg'])
                    # pointData.append(values["dates"][list(values["dates"].keys())[-1]]['avg'])
                        
            d[mod] = {"model": mod,"dates":values['dates'],
                      'change':abs(float(change)), 'changecolor': changecolor,
                      'change_30':abs(float(change_30)), 'changecolor_30': changecolor_30,
                      "price": round(mean_price, 0),
                     'pointData':pointData, 'labelData':labelData, 'market_liquidity':marketing_liquidity,
                    "year": most_common_year,'brand': most_common_brand, "circulating_supply": circulating_supply, 'actual_circulating_supply': circulating_supply, 
                    "name": most_common_name, "image":values["image"], 'stockId':values['stockId'] }
    print(all_count, good_count, bad_count,un_avail_count,'this')
    new_list = list(d.values())
    watch_dict['is_watch_data_processed'] = True
    watch_dict['processed_watch_data'] = new_list
    return new_list

def int_sum(my_list): # suns an array potentially containing strings
    total = 0
    for item in my_list:
        try:
            total += int(item)
        except ValueError:
            pass
    
    return total

def get_single_watch(model_number):
    data = None
    if 'filtered_list' in watch_dict.keys():
        data = watch_dict
    else:
        processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
        if processedfile not in os.listdir(os.getcwd()):
            preload()
        with open(os.path.join(os.getcwd(), processedfile)) as json_file:
            processed_jsondata = json.load(json_file) 
            data = processed_jsondata['watch_dict']
            for key, value in data.item():
                watch_dict[key] = value

    if model_number in single_watch_dict.keys():
        return single_watch_dict[model_number]
    
    pre_data = {"id": model_number, "prices": [], "years": [], "names": [], "image":'', "dates":{}}
    # singleData = watch.query.filter_by(modelNumber=model_number).all()
    singleData = [watch for watch in all_watches if watch.modelNumber == model_number]

    for datum in singleData:
        item = serializeWatch(datum)
        pre_data["prices"].append(int(item['price']))
        pre_data["years"].append(item['year'])
        pre_data["names"].append(item['series'])
        pre_data["image"] = item['image']
        pre_data["stockId"] = item['stockId']
        if item['dateString'] in pre_data['dates'].keys():
            pre_data["dates"][item['dateString']]['prices'].append(int(item['price']))
            pre_data["dates"][item['dateString']]['avg'] = sum(pre_data["dates"][item['dateString']]['prices'])/len(pre_data["dates"][item['dateString']]['prices'])
            pre_data["dates"][item['dateString']]['max'] = min(pre_data["dates"][item['dateString']]['prices'])
            pre_data["dates"][item['dateString']]['max'] = max(pre_data["dates"][item['dateString']]['prices'])
            pre_data["dates"][item['dateString']]['sum'] = sum(pre_data["dates"][item['dateString']]['prices'])

        else:
            pre_data["dates"][item['dateString']] = {'prices':[int(item['price'])], 'avg': int(item['price']), 'min': int(item['price']), 'max': int(item['price'])}
    

    if len(pre_data["prices"]) > 0:
        pre_data["mean_price"] = stats.mean(pre_data["prices"])
        pre_data["min_price"] = min(pre_data["prices"])
        pre_data["max_price"] = max(pre_data["prices"])
        pre_data["most_common_year"] = Counter(pre_data["years"]).most_common(1)[0][0]
        pre_data["most_common_name"] = Counter(pre_data["names"]).most_common(1)[0][0]
    else:
        pre_data["mean_price"] = 0
        pre_data["min_price"] = 0
        pre_data["most_common_year"] = 0
        pre_data["max_price"] = 0
        pre_data["most_common_name"] = 0


    pre_data["actual_circulating_supply"] = len(list(pre_data["prices"])) 
  
    pre_data["circulating_prices"] = []
    pre_data["circulating_prices_dates"] = []
    pre_data["circulating_data"] = []

    added_variant = {}
    circulating_data = []
    for datum in singleData:
        item = serializeWatch(datum)
        if item['url'].split('/')[4] not in added_variant:
            pre_data["circulating_prices"].append(int(item['price'])) 
            circulating_data.append(item) 
            added_variant[item['url'].split('/')[4]] = [int(item['price'])]
        else:
            pre_data["circulating_prices"].append(int(item['price']))
            added_variant[item['url'].split('/')[4]].append(int(item['price']))

    # print(added_variant)
    # print(circulating_data)
    for key, prices in added_variant.items():
        for item in circulating_data:
            if item['url'].split('/')[4] == key:
                pre_item = item
                pre_data['price']  = stats.mean(prices)
                pre_data["circulating_data"].append(item)
                
    date_array = list(pre_data["dates"].keys())
    date_array.sort()
    
    pre_data["last_updated"] = ''
    if len(date_array) > 0:
        pre_data["last_updated"] = date_array[-1]
    pre_data["circulating_supply"] = len(list(pre_data["prices"]))
    pre_data["market_liquidity"] = int_sum(list(pre_data["circulating_prices"]))
    print(pre_data)
    # import pprint 
    # pprint.pprint(pre_data)
    single_watch_dict[model_number] = pre_data
    return pre_data

@app.route('/portfolio/<string:user_id>', methods=['GET', 'POST', 'PUT'])
def manage_portfolio(user_id):
    if request.method == 'GET':
        return get_user_portfolio_data(user_id)
    elif request.method == 'POST':
        return add_to_portfolio(user_id)
    elif request.method == 'PUT':
        return update_portfolio_item(user_id)

def get_user_portfolio_data(user_id):
    try:
        portfolio_items = customer_watches.query.filter_by(user_id=user_id, deleted=False).all()

        portfolio_data = []
        for item in portfolio_items:
            instrument = Instruments.query.filter_by(modelNumber=item.modelNumber).first()
            if instrument:
                portfolio_data.append({
                    'portfolio_id': item.id,
                    'user_id': str(item.user_id),
                    'brand': item.brand,
                    'modelNumber': item.modelNumber,
                    'series': item.series,
                    'year': item.year,
                    'box': item.box,
                    'price': item.price,
                    'watch_price': instrument.price,
                    'owned':item.owned,
                    # Add more fields as needed
                })
            else:   
                 portfolio_data.append({
                    'portfolio_id': item.id,
                    'user_id': str(item.user_id),
                    'brand': item.brand,
                    'modelNumber': item.modelNumber,
                    'series': item.series,
                    'year': item.year,
                    'box': item.box,
                    'price': item.price,
                    'watch_price': 0,
                    'owned':item.owned,
                    # Add more fields as needed
                })

        return jsonify({'portfolio': portfolio_data, 'message': 'Portfolio data retrieved successfully', 'status': 200})

    except SQLAlchemyError as e:
        return jsonify({'message': 'Error while retrieving portfolio data', 'status': 500})

def add_to_portfolio(user_id):
    try:
        data = request.json
        modelNumber = data.get('modelNumber')
        brand = data.get('brand')
        series = data.get('series')
        year = data.get('year')
        box = data.get('box')
        price = data.get('price')
        soldPrice = data.get('soldPrice')
        deleted = data.get('deleted')
        owned=data.get('owned')
        
        # Create a new portfolio item
        new_portfolio_item = customer_watches(
            user_id=user_id,
            brand=brand,
            modelNumber=modelNumber,
            series=series,
            year=year,
            box=box,
            price=price,
            soldPrice = soldPrice,
            deleted= deleted,
            owned= owned
        )
        db.session.add(new_portfolio_item)
        db.session.commit()

        return jsonify({'message': 'Item added to portfolio', 'status': 201})

    except SQLAlchemyError as e:
        print("Error:", e)
        return jsonify({'message': 'Error while adding item to portfolio', 'status': 500})
    

def update_portfolio_item(user_id):
    try:
        data = request.json
        portfolio_id = data.get('portfolio_id')
        soldPrice = data.get('soldPrice')
        deleted = data.get('deleted')
        owned = data.get('owned')
        # Get the portfolio item by portfolio_id and user_id
        portfolio_item = customer_watches.query.filter_by(id=portfolio_id, user_id=user_id, deleted=False).first()
        if not portfolio_item:
            return jsonify({'message': 'Portfolio item not found', 'status': 404})

        # Update the portfolio item
        portfolio_item.soldPrice = soldPrice
        portfolio_item.deleted = deleted
        portfolio_item.owned = owned
        db.session.commit()

        return jsonify({'message': 'Portfolio item updated', 'status': 200})

    except SQLAlchemyError as e:
        print("Error:", e)
        return jsonify({'message': 'Error while updating portfolio item', 'status': 500})
    
# Route for user signup
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    phone_number = request.json.get('phone_number')
    
    hashed_password = generate_password_hash(password, method='sha256')

    existing_email = User_details.query.filter_by(email=email).first()

    if existing_email:
        return jsonify({'message': 'Email already exists. Please log in.', 'status': 409}), 409
    
    user = User_details(username=username, password=hashed_password, email=email)
    profile = Profile(user_id=user.user_id, phone_number=phone_number)
    
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({'message': 'User successfully registered!', 'status': 200})

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = User_details.query.filter_by(email=email).first()
    
    if  user and check_password_hash(user.password, password):
        session['user_id'] = user.user_id
        return jsonify({'message': 'Ok','user_id':user.user_id ,'status': 200})
    else:
        return jsonify({'message': 'Invalid username or password', 'status': 401})

# # Route for user logout
# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return jsonify({'message': 'Logged out successfully!', 'status': 200})

           

@app.route("/debugging")
def debugging():
    return 'Debugging'

@app.route('/react_view_watch')
def react_view_watch():
    if 'chart_data' not in watch_dict.keys():
        preload()
    model_number = request.args.get('model')
    
    data = get_single_watch(model_number)
    return jsonify({'response':data,'message':'Data Loaded For Watch','status':200})
    

@app.route('/react_view_all_images')
def react_view_all_images():
    f = open(os.path.join(os.getcwd(),'downloadedimagelist.txt') , 'r')
    downloaded_data = f.readlines()
    
    f.close()
    new_downloaded_data = []
    for item in downloaded_data:
        new_downloaded_data.append(item.replace('\n',''))

    return jsonify({'response':new_downloaded_data,'message':'Images obtained','status':200})
@app.route('/react_view_all_watches')
def react_view_all_watches():
    if 'chart_data' not in watch_dict.keys():
        preload()
    # return jsonify({'data':m})
    if f"processed{str(datetime.datetime.today()).split(' ')[0]}.json" not in os.listdir(os.getcwd()):
        preload()
    processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
    with open(os.path.join(os.getcwd(), processedfile)) as json_file:
        processed_jsondata = json.load(json_file) 
        sorted_data = sorted(processed_jsondata['data'], key=lambda x: x["change"], reverse=True)
        return jsonify({'response':{"data":sorted_data, "price_data":processed_jsondata['price_data'], 
                                "market_cap_data":processed_jsondata['market_cap_data'], "chart":processed_jsondata['chart']},
                                'message':'Data Loaded For all Watches','status':200})
    


@app.route('/react_view_filtered_watches')
def react_view_filtered_watches():
    # item = get_item_by_id(item_id)
    preload()
    sort_param = request.args.get('filterby')
    data = None
    if 'filtered_list' in watch_dict.keys():
        data = {'chart_data':watch_dict['chart_data'], 
                'total_market_cap_chart':watch_dict['total_market_cap_chart'],
                'total_market_cap': watch_dict['total_market_cap'],
                'total_market_cap_yesterday': watch_dict['total_market_cap_yesterday'],
                'filtered_list':watch_dict['filtered_list'], 
                'latest_file_filtered_list': watch_dict['latest_file_filtered_list'],
                'market_cap_data': watch_dict['market_cap_data'],
                'date_list':  watch_dict['date_list']
                }  
    else:
        data = fetch_data()   
    new_list = None
    if 'is_watch_data_processed' in watch_dict.keys():
        new_list = watch_dict['processed_watch_data']
    else:
        new_list = process_all_data(data)
        watch_dict['processed_watch_data'] = new_list
        watch_dict['is_watch_data_processed'] = True

    filterd_data = None
    sorted_data = None
    asc = None
    if asc: 
        sorted_data = sorted(new_list, key=lambda x: x[sort_param])
    else:
        sorted_data = sorted(new_list, key=lambda x: x[sort_param], reverse=True)
    return jsonify({'response':{"data":sorted_data},'message':'Data Loaded For all Watches','status':200})


@app.route('/react_view_sorted_watches')
def react_view_sorted_watches():
    processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
    with open(os.path.join(os.getcwd(), processedfile)) as json_file:
        processed_jsondata = json.load(json_file) 
        sort_param = request.args.get('sortby')
        asc = request.args.get('asc')
        
        sorted_data = None
        if asc == 'true': 
            sorted_data = sorted(processed_jsondata['data'], key=lambda x: x[sort_param])
        else:
            sorted_data = sorted(processed_jsondata['data'], key=lambda x: x[sort_param], reverse=True)


        return jsonify({'response':{"data":sorted_data},'message':'Data Loaded For all Watches','status':200})

@app.route('/view_watch/<model_number>')
def view_watch(model_number):
    
    # item = get_item_by_id(item_id)
    data = get_single_watch(model_number)
    return render_template('public/watch.html', data=data)

@app.route('/all_data/<model_number>')
def all_data(model_number):
    data = fetch_data()
    all_watches = []
    for item in data['filtered_list']:
        if item['modelNumber'] == model_number:
            all_watches.append(item)
    return jsonify({'variants':all_watches, 'count':len(all_watches)})



def preload_image():
    # all_watches = watch.query.all()
    imageDict = {}
    count = 0
    imageSet = set()
    stockSet = set()
    for item in all_watches:
        imageSet.add(item.image)
        stockSet.add(item.stockId)
        imageDict[item.stockId] =item.image
    watch_dict['image_list'] = imageDict

    return imageDict
def boolify(value):
    if value == 'Yes':
        return True
    return False

def datify(value): # receives a datetime object
    return f"{value.year}-{value.month}-{value.day}"
def makeDate(value):
    n = value.split('-')
    date = datetime.datetime(int(n[0]), int(n[1]), int(n[2]))
    return date

@app.route('/migrate')
def mirgate_data(): # function to preload some watch data
    print('migrating')
    d = {}
    duplicated = 0
    filtered_list = []
    # date_list = []
    sorted_dir_list = os.listdir(os.path.join(os.getcwd(), 'allwatches'))
    watch_dict['file_list'] = sorted_dir_list
    sorted_dir_list.sort()
    watch_dict['file_list'] = sorted_dir_list
    if 'migratedfiles.txt' not in os.listdir(os.getcwd()): 
        f = open(os.path.join(os.getcwd(),'migratedfiles.txt'),'w')
        f.close()
    
    f = open(os.path.join(os.getcwd(),'migratedfiles.txt') , 'r')
    migrated_data = f.readlines()
    f.close()
    new_sorted_dir_list = [item for item in sorted_dir_list if f'{item}\n' not in migrated_data ]
    
    
    print("list of file going to migrate",new_sorted_dir_list)
    for item in new_sorted_dir_list:  #gets a list of all the files in the folder
        print("migrating", item)
        try:
            with open(os.path.join(os.getcwd(), 'allwatches', item),'r') as f: #opens all files within the loop
                # date_list.append(item.split('_')[3].split('.')[0])
                 

                data = f.read()     
                a_list = json.loads(data)  
                for watch_item in a_list:                 # data is looped through
                    watch_item.pop('timestamp')           # the timestamp data has to be removed at it was the only parameter that made duplicate data differnt and undetectable
                    if watch_item not in filtered_list:   # confirms there is no duplicate
                        pre_watch_item = watch_item
                        pre_watch_item['date'] = item.split('_')[3].split('.')[0] 
                        filtered_list.append(pre_watch_item)  # dappends the item if it doesnt exist in the list
                        isCartier = False
                        if 'isCartierPartnership' in watch_item.keys():
                            isCartier = watch_item['isCartierPartnership']
                        n = pre_watch_item['date'].split('-')
                        date = datetime.datetime(int(n[0]), int(n[1]), int(n[2]))
                        
                        node = Nodes.query.filter_by(brand=watch_item['brand']).first()
                        if node is None:
                            # Create a new brand record
                            node = Nodes(brand=watch_item['brand'],created_at=date,name=watch_item['brand'])
                            db.session.add(node)
                            # Update other attributes as needed
                            
                        db.session.commit()

                        market = Markets.query.filter_by(series=watch_item['series']).first()
                        if market is None:
                            # Create a new brand record
                            market = Markets(node_id = node.node_id ,
                                            created_at=date, 
                                            brand=node.brand, 
                                            seriesGroup=watch_item['seriesGroup'], 
                                            series=watch_item['series'] ,
                                            name=watch_item['series'],
                                            seriesUrl = watch_item['seriesUrl'],
                                            )
                            db.session.add(market)
                            # Update other attributes as needed
                            
                        db.session.commit()

                        instrument = Instruments.query.filter_by(modelNumber=watch_item['modelNumber']).first()
                        if instrument is None:
                            # Create a new brand record
                            instrument = Instruments(
                                                market_id = market.market_id,
                                                created_at=date,
                                                modelNumber=watch_item['modelNumber'],
                                                name=watch_item['modelNumber'],
                                                seriesGroup=market.seriesGroup, 
                                                series=market.series, 
                                                modelUrl = watch_item['modelUrl'],
                                                year=convert_to_bool_year(watch_item['year']),
                                                )
                            db.session.add(instrument)
                            # Update other attributes as needed
                            
                        db.session.commit()

                        watch = Watches.query.filter_by(stockId=str(watch_item['stockId'])).first()
                        if watch is None:
                            watch = Watches(modelNumber=instrument.modelNumber,
                                          instrument_id = instrument.instrument_id, 
                                                stockId=watch_item['stockId'], 
                                                image=watch_item['image'],
                                                url=watch_item['url'],
                                                date = date,
                                                dateString= pre_watch_item['date'],
                                                box=convert_to_bool(watch_item['box']),
                                                papers=convert_to_bool(watch_item['papers']),
                                                material=watch_item['material'], strap=watch_item['strap'],
                                                itemTypeDescription=watch_item['itemTypeDescription'], dial=watch_item['dial'],
                                                limitedEdition= convert_to_bool(watch_item['limitedEdition']),
                                                caseSize=watch_item['caseSize'], 
                                                price=watch_item['price'],
                                                discountMargin=watch_item['discountMargin'],
                                                isComingSoon=watch_item['isComingSoon'],
                                                isDiscounted=watch_item['isDiscounted'],
                                                isSold=watch_item['isSold'],
                                                isPublished=watch_item['isPublished'],
                                                isPriceOnApplication=watch_item['isPriceOnApplication'],
                                                isCurrentlyPresale=watch_item['isCurrentlyInPresale'],
                                                isCartierPartnership=isCartier
                                                )

                            db.session.add(watch)
                            
                        else:
                            # Update existing brand attributes (if needed)
                            if watch.price != watch_item['price']:
                                watch.date = date,
                                watch.dateString= pre_watch_item['date'],
                                watch.price = watch_item['price']
                            # Update other attributes as needed
                        # print("runn before going to trigger")
                        db.session.commit()

                        

                        
                    else:
                        duplicated += 1
            f = open(os.path.join(os.getcwd(),'migratedfiles.txt') , 'a')
            f.write(f'\n{item}')
            f.close()  
            print('migrated', item)
        except Exception as E:
            print('could not migrate', item, 'error' , str(E))
    db.session.commit()
    print('migrated successfully')
    return ('migrated successfully')

@app.route('/get_new_images')
def fetch_images():
    preload_image()
    return render_template('public/images.html') 

@app.route('/image_log')
def get_image_log():
    return jsonify({'info': watch_dict['logInfo']})

@app.route('/image_downloader')
def download_images():
    import time 
    # preload()
    preload_image()
    watch_dict['logInfo'] = 'intialized download'
    print('intialized download')
    downloaded_images = []
    count = 0
    imagelist = {}
    if 'image_list' in watch_dict.keys():
        imagelist = watch_dict['image_list']
    else:
        imagelist = preload_image()

    if 'downloadedimagelist.txt' not in os.listdir(os.path.join(os.getcwd())):
        f = open(os.path.join(os.getcwd(),'downloadedimagelist.txt') , 'w')   
        f.close() 

    f = open(os.path.join(os.getcwd(),'downloadedimagelist.txt') , 'r')   
    download_images = f.readlines()
    f.close()
    non_downloaded_images = [item for item in imagelist.keys() if f'{item}\n' 
                             not in download_images and item.split('.')[0] not in os.listdir(os.path.join(os.getcwd(), 'static','images'))]
    no_dash_count = 0
    for item in non_downloaded_images:
        watch_dict['logInfo'] = f"Downloading {count} of {len(non_downloaded_images)}: url: {item}"
        print(f"Downloading {count} of {len(non_downloaded_images)}: url: {item}")
        try:
            response = requests.get(imagelist[item])
            open(os.path.join(os.getcwd(), 'static','images',f"{item}.jpg"), "wb").write(response.content)
            f = open(os.path.join(os.getcwd(),'downloadedimagelist.txt') , 'a')
            f.write(f'\n{item}')
            f.close()    
            count += 1
            watch_dict['logInfo'] = f"Downloaded {count} of {len(non_downloaded_images)}: url: {item}"
        except:
            count += 1
            watch_dict['logInfo'] = f"Counld not Download url: {item}"
    f.close()
    print('downloaded all')
    watch_dict['logInfo'] = f"Downloaded all"
    return jsonify({'info':'completed'})

@app.route('/all_data_new/<model_number>')
def all_data_new(model_number):
    all_watches = []
    d = {}
    duplicated = 0
    filtered_list = []

    sorted_dir_list = os.listdir(os.path.join(os.getcwd(), 'allwatches'))
    sorted_dir_list.sort()
    for item in sorted_dir_list[-7:]:  #gets a list of all the files in the folder
        total_prices =0 
        with open(os.path.join(os.getcwd(), 'allwatches', item),'r') as f: #opens all files within the loop
            data = f.read()     
            a_list = json.loads(data)  
            for watch_item in a_list:                 # data is looped through
                total_prices += int(watch_item['price'])
                if watch_item not in filtered_list:   # confirms there is no duplicate
                    pre_watch_item = watch_item
                    pre_watch_item['date'] = item.split('_')[3].split('.')[0]
                    filtered_list.append(pre_watch_item)  # dappends the item if it doesnt exist in the list
                else:
                    duplicated += 1
    for item in filtered_list:
        if item['modelNumber'] == model_number:
            all_watches.append(item)
    return jsonify({'variants':all_watches, 'count':len(all_watches)})

@app.route('/current_watch_data/<model_number>')
def watch_data(model_number):
    # item = get_item_by_id(item_id)
    data = get_single_watch(model_number)['circulating_data']
    return jsonify({'variants':data, 'count':len(data)})

@app.route("/indices")
def indices():
    processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
    with open(os.path.join(os.getcwd(), processedfile)) as json_file:
        processed_jsondata = json.load(json_file)  
        return jsonify({'response':{'data':processed_jsondata['indices_data']},'message':'Indices Loaded For all Watches','status':200})

@app.route("/performers")
def performers():
    processedfile = f"processed{str(datetime.datetime.today()).split(' ')[0]}.json"
    with open(os.path.join(os.getcwd(), processedfile)) as json_file:
        processed_jsondata = json.load(json_file) 
        return jsonify({'response':{'performers':processed_jsondata['performer_data']},'message':'Performers Loaded For all Watches','status':200})

@app.route('/parform')
def fetch_parformers():
    preload()
    d = {}
    new_d = []
    # print(watch_dict.keys())
    # p_data = fetch_data()
    p_data = process_all_data(watch_dict)
    return jsonify({'data':p_data})
    for item in watch_dict['filtered_list']:
        d.setdefault(item['modelNumber'], {'dates':{}, 'image':item['image'], 'brand':item['brand'], 'stockId':item['stockId']})
        if item['dateString'] in d[item['modelNumber']]["dates"].keys():
            if int(item['price']) > 0:
                d[item['modelNumber']]["dates"][item['dateString']]['prices'].append(int(item['price']))
                d[item['modelNumber']]["dates"][item['dateString']]['avg'] = sum(d[item['modelNumber']]["dates"][item['dateString']]['prices'])/len(d[item['modelNumber']]["dates"][item['dateString']]['prices'])
        else:
            d[item['modelNumber']]["dates"][item['dateString']] = {'prices':[int(item['price'])], 'avg': int(item['price']),}
    # print(d)

    # print('fetch performers', len(watch_dict['filtered_list']))
    
    for mod, values in d.items():
        date_array = list(values["dates"].keys())
        date_array.sort()
        final_data = 0
        start_avg = 0
        end_avg = 0
        try:
            # final_data = values["dates"][date_array[-1]] 
            # data['date_list'][-7:] #
            if  watch_dict['date_list'][-7:][0] in date_array:
                start_avg = values["dates"][watch_dict['date_list'][-7:][0]]['avg'] 
            if date_array[-1] in watch_dict['date_list'][-7:]:
                end_avg = values["dates"][date_array[-1]]['avg'] 

            pre_val = (end_avg - start_avg)/start_avg*100
            val = str((end_avg - start_avg)/start_avg*100)
            m_val = f"{val.split('.')[0]}.{val.split('.')[1][:2]}"         
        except Exception as E:
            pre_val = 0
            val = str(0)
            m_val = 0
        change = m_val
        changecolor = None
        neg = True
        if pre_val > 0.1:
            neg = False           
        new_d.append({"model": mod,"image":values['image'], 'stockId':values['stockId'],'brand': values['brand'], 'change':change, 'negative': neg, 'start': start_avg, 'end':end_avg, 'start_date': watch_dict['date_list'][-7:][0], 'end_date':date_array[-1]})
    
    top_bad_performers = {}
    top_good_performers = {}
    for item in new_d:
        if item['negative']:
            top_bad_performers[float(item['change'])] = new_d.index(item)
        else:
            top_good_performers[float(item['change'])] = new_d.index(item)
    sorted_top_bad_performances = list(top_bad_performers.keys())
    sorted_top_bad_performances.sort()
    sorted_top_bad_performances = sorted_top_bad_performances[:10]

    sorted_top_good_performances = list(top_good_performers.keys())
    sorted_top_good_performances.sort(reverse=True)
    sorted_top_good_performances = sorted_top_good_performances[:10]
    # print(sorted_top_bad_performances)
    # print(sorted_top_good_performances)    

    bad_performance_models = []
    good_performance_models = []

    for change in sorted_top_bad_performances:
        bad_performance_models.append(new_d[top_bad_performers[change]])
    for change  in sorted_top_good_performances:
        good_performance_models.append(new_d[top_good_performers[change]])        

    watch_dict["positive_performance_models"] = good_performance_models
    watch_dict["negative_performance_models"] = bad_performance_models
    return {"positive_performance_models":good_performance_models, "negative_performance_models":bad_performance_models}
    

@app.route("/")
def home():
       
    data = None
    if 'filtered_list' in watch_dict.keys():
        data = {'chart_data':watch_dict['chart_data'], 
                'total_market_cap_chart':watch_dict['total_market_cap_chart'],
                'total_market_cap': watch_dict['total_market_cap'],
                'total_market_cap_yesterday': watch_dict['total_market_cap_yesterday'],
                'filtered_list':watch_dict['filtered_list'], 
                'latest_file_filtered_list': watch_dict['latest_file_filtered_list'],
                'market_cap_data': watch_dict['market_cap_data'],
                'date_list':  watch_dict['date_list']
                }  
    else:
        data = fetch_data()    

    new_list = None
    if 'is_watch_data_processed' in watch_dict.keys():
        new_list = watch_dict['processed_watch_data']
    else:
        new_list = process_all_data(data)
        watch_dict['processed_watch_data'] = new_list
        watch_dict['is_watch_data_processed'] = True

    sorted_data = sorted(new_list, key=lambda x: x["price"], reverse=True)
    chart = {'total_market_cap_chart': data['total_market_cap_chart']} 

    return render_template("public/home.html", data=new_list[:100], price_data= data['chart_data'], market_cap_data = data['market_cap_data'], chart=chart)

@app.route('/view_item/<int:item_id>')
def view_item(item_id):
    item = get_item_by_id(item_id)
    return render_template('public/home.html', item=item)

@app.route("/about")
def about():
    return render_template("public/about.html")

@app.route("/mynetworth")
def mynetworth():
    return render_template("public/mynetworth.html")

@app.route("/priceme",methods=['GET', 'POST'])
def priceme():
    # open json, this will need ammending to open 'x' ammount back. For now i will load the latest  .json manually.
    with open(
            "PLACE JSON PATH HERE",
            'r') as f:
        data = f.read()
        # print(data)
    # Cconvert the 'saved' jason back to a python list
    # print(t)
    a_list = json.loads(data)

    d = {}

    for item in a_list:
        d.setdefault(item['modelNumber'], {"prices": [], "years": [], "names": []})
        d[item['modelNumber']]["prices"].append(int(item['price']))
        d[item['modelNumber']]["years"].append(item['year'])
        d[item['modelNumber']]["names"].append(item['series'])
        

    for mod, values in d.items():
        mean_price = stats.mean(values["prices"])
        most_common_year = Counter(values["years"]).most_common(1)[0][0]
        most_common_name = Counter(values["names"]).most_common(1)[0][0]
        d[mod] = {"model": mod, "price": round(mean_price, 0), "year": most_common_year, "name": most_common_name}

    new_list = list(d.values())
    for item in new_list:
        try:
            model = item['model']
            model = model.split()[0]
            item['model'] = int(model)
        except ValueError:
            print(f"{item} could not be converted to integer")

    for item in new_list:
        try:
            model_string = str(item['model'])
            model = int(''.join(filter(str.isdigit, model_string)))
            item['model'] = model
        except ValueError:
            print(f"{item} could not be converted to integer")
    sorted_data = sorted(new_list, key=lambda x: x["price"], reverse=True)
    for i, item in enumerate(sorted_data, 1):
        item["rank"] = i
    # # return render_template("public/home.html", data=data, plot=plot )
    # return render_template("public/home.html", data=new_list)

    # print("Form data:", request.form)
    if request.method == 'POST':
        print(f"Received POST request: {request.url}")
        # handle the POST request
        print(request.form)
        # add additional code to process the form data here
        mod = int(request.form['model_number'])
        # print(mod)
        price = None
        for watch in new_list:
            if watch['model'] == mod:
                price = watch['price']
                break
        if price is not None:
            print("Price:", price)
        else:
            print("Watch not found.")

        return render_template("public/priceme.html" ,mod=mod, price=price)
    elif request.method == 'GET':
        # handle the GET request
        return render_template("public/priceme.html")
    else:
        # return an error for other methods
        return "Method Not Allowed", 405


@app.route("/jinja")
def jinja():

    my_name = "reece"
    age = 30
    langs = ["python","java","bash","ruby"]
    friends={
        "Tom":30,
        "Amy":50,
        "reece":10

    }
    cool = True

    class GitRemote:
        def __init__(self,name,description, url):
            self.name = name
            self.description = description
            self.url = url
        def pull(self):
            return f"pulling repo {self.name}"
        def clone(self):
            return f"cloning into{self.url}"

    my_remote=GitRemote(
        name='Flask Jinja',
        description='Template design tutorial',
        url="https//github.com/",

    )

    def repeat(x, qty):
        return x * qty


    return(render_template("public/jinja.html", my_name=my_name, age=age,
                           langs=langs, friends=friends, cool=cool,
                           GitRemote=GitRemote,repeat=repeat, my_remote=my_remote))


# preload()

@app.route("/signup")
def sign_up():
    if request.method=="POST":

        req = request.form

        print(req)

        return redirect(request.url)

    return render_template("public/sign_up.html")

# @ app.route('/')
# def hello():
#     nodes=Node.query.all()
#     # Query all watch data from the three tables using a join
#     all_watches = db.session.query(Node, Market, Instrument).\
#     join(Market, Node.id == Market.node_id).\
#     join(Instrument, Market.id == Instrument.market_id).\
#     all()
#     node_data = [{'id': node.id, 'brand': node.brand, 'seriesGroup': node.seriesGroup, 'series': node.series} for node in nodes]
#     # Create a list of data objects
#     watches_data = []

#     for node, market, instrument in all_watches:
#         watch_data = {
#             'node_id': node.id,
#             'brand': node.brand,
#             'seriesGroup': node.seriesGroup,
#             'series': node.series,
#             'market_id': market.id,
#             'modelNumber': market.modelNumber,
#             'box': market.box,
#             'papers': market.papers,
#             'limitedEdition': market.limitedEdition,
#             'year': market.year,
#             'stockId': instrument.stockId,
#             'image': instrument.image,
#             'url': instrument.url,
#             'date': instrument.date,
#             'dateString': instrument.dateString,
#             'material': instrument.material,
#             'strap': instrument.strap,
#             'itemTypeDescription': instrument.itemTypeDescription,
#             'dial': instrument.dial,
#             'caseSize': instrument.caseSize,
#             'price': instrument.price,
#             'discountMargin': instrument.discountMargin,
#             'isComingSoon': instrument.isComingSoon,
#             'isDiscounted': instrument.isDiscounted,
#             'isSold': instrument.isSold,
#             'isPublished': instrument.isPublished,
#             'isPriceOnApplication': instrument.isPriceOnApplication,
#             'isCurrentlyPresale': instrument.isCurrentlyPresale,
#             'isCartierPartnership': instrument.isCartierPartnership
#         }
#         watches_data.append(watch_data)

#     # print(watches_data)
#     return jsonify(watches_data)

if __name__ == '__main__': 
    app.run(debug=True)