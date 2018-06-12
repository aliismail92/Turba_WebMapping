from flask import Flask, render_template,request,redirect,flash
import folium
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func



app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/mapping_data'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fhjufkgdwehwtu:ea7af78868816f4d0c810fe7fd3438b466ea80f3572e409550edc4b55da0c872@ec2-54-204-18-53.compute-1.amazonaws.com:5432/d4j4eff77bq1ul?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
db.init_app(app)
db.app=app

#app.config.from_pyfile('./config.py')
global message_coord
message_coord = ""

class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer,primary_key=True)
    name_=db.Column(db.String(120),unique=True)
    coord_=db.Column(db.String(120))
    source_=db.Column(db.String(120))
    quantities_=db.Column(db.Integer)

    def __init__(self,name_,coord_,source_,quantities_):
        self.name_=name_
        self.coord_=coord_
        self.source_=source_
        self.quantities_=quantities_

def Mapping():
    global fig

    with app.app_context():
        count = db.session.query(Data.name_).count()

        fig = folium.Figure(width=1000, height=200)
        map = folium.Map(location=[33.811257, 35.605018], zoom_start=14, tiles='OpenStreetMap')
        org = folium.FeatureGroup(name="Green")
        carbsour = folium.FeatureGroup(name="Brown")

        for i in range(count):

            name = db.session.query(Data.name_)[i][0]
            coord= db.session.query(Data.coord_)[i][0].split(",")

            try:

                lat = float(coord[0])
                lon = float(coord[1])
                res = db.session.query(Data.source_)[i][0]

                if res == "Brown":
                    html ='<p>Resource : Brown</p>'
                    test = folium.Html("Name: "+name+html, script=True)
                    popup = folium.Popup(test)

                    carbsour.add_child(folium.Marker(location=[lat, lon],popup = popup,icon=folium.Icon(color='darkred')))

                elif res == "Green":
                    html ='<p>Resource : Green</p>'
                    test = folium.Html("Name: "+name+html, script=True)
                    popup = folium.Popup(test)
                    popup = folium.Popup(test, max_width=400)
                    org.add_child(folium.Marker(location=[lat, lon],popup =popup,icon=folium.Icon(color='green')))
            except:
                message_coord= "Warning: Coordinates are not numerical values"
        map.add_child(org)
        map.add_child(carbsour)
        map.add_child(folium.LayerControl())
        fig.add_child(map)

def Table():
    global table
    with app.app_context():
        count = db.session.query(Data.name_).count()
        table = pd.DataFrame(columns=["Name","Coordinates","Resrource"], index = list(range(count)))
        for i in range(count):

            name = db.session.query(Data.name_)[i][0]
            coord= db.session.query(Data.coord_)[i][0]
            res = db.session.query(Data.source_)[i][0]
            #quan = db.session.query(Data.quantities_)[i][0]

            table.loc[i]=[name,coord,res]
    return table

app= Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method=='POST':
        name = request.form["location_name"]
        coord = request.form["location_coord"]
        resource = request.form["location_resource"]
        quantities = request.form["location_quantities"]

        if db.session.query(Data).filter(Data.name_==name).count()==0:
                data = Data(name, coord, resource, quantities)
                db.session.add(data)
                db.session.commit()

        else:
            error = "Name Already Exists"
            return render_template("index.html", text="Name Already Exists",table = table.to_html())
    Table()
    print(message_coord)
    return render_template("index.html",text = message_coord, table = table.to_html())


@app.route('/map')
def map():
    Mapping()

    return fig.get_root().render()

if __name__=="__main__":
    app.run(debug=True)
