from flask import Flask, jsonify, render_template, redirect
import pymongo
import scrape_mars

# Use flask_pymongo to set up mongo connection
app = Flask(__name__)
conn = 'mongodb://localhost:27017/mars_db'
client = pymongo.MongoClient(conn)


# route
@app.route("/")
def index():
    db = client.mars_db
    mars = db.mars
    return render_template("index.html", mars = mars.find_one())

@app.route("/scrape")
def scrape():
    
    db = client.mars_db
    mars = db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)