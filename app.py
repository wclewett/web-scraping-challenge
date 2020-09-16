from flask import Flask, jsonify, render_template
import pymongo
import scrape_mars

# Use flask_pymongo to set up mongo connection
app = Flask(__name__)
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# route
@app.route("/")
def index():
    mars = client.db.mars.find_one()
    # print(mars)
    return render_template("index.html", mars = mars)

@app.route("/scrape")
def scrape():
    
    mars = client.db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)