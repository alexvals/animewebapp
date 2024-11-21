from flask import Flask, render_template, request, redirect, abort
import sqlite3

app = Flask(__name__)
app.secret_key = "who_is_out_here_pooping"

def get_db_connection():
    connection = sqlite3.connect("AnimeDB.db")
    connection.row_factory = sqlite3.Row
    return connection

def get_order_by(results):
    order = request.args.get("order", "Score ASC, Rank DESC")
    if order not in ["Score DESC, Rank ASC", "Score ASC, Rank DESC", "Name", "Name DESC", "Synopsis", "Synopsis DESC"]:
        order = "Score ASC, Rank DESC"
    if order != "Score ASC, Rank DESC":
        results = [dict(row) for row in results]
        if order == "Score DESC, Rank ASC":
            results = sorted(results, key=lambda x: x["Rank"], reverse=True)
        elif order == "Name":
            results = sorted(results, key=lambda x: x["Name"])
        elif order == "Name DESC":
            results = sorted(results, key=lambda x: x["Name"], reverse=True)
        elif order == "Synopsis":
            results = sorted(results, key=lambda x: x["Synopsis"])
        else:
            results = sorted(results, key=lambda x: x["Synopsis"], reverse=True)
    validUrls = ["?sort_by=Rank&order=Score%20ASC,%20Rank%20DESC", "/?sort_by=Rank&order=Score%20DESC,%20Rank%20ASC",
    "/?sort_by=Name&order=Name", "/?sort_by=Name&order=Name%20DESC",
    "/?sort_by=Synopsis&order=Synopsis", "/?sort_by=Synopsis&order=Synopsis%20DESC"]
    definedUrl = any(url in request.full_path for url in validUrls)
    return order, results, definedUrl

@app.errorhandler(404)
def home(e):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Name, Rank, Synopsis FROM animedataset2023 ORDER BY Score DESC, Rank ASC LIMIT 10")
    results = cursor.fetchall()
    error = None
    validUrls = ["?sort_by=Rank&order=Score%20ASC,%20Rank%20DESC", "/?sort_by=Rank&order=Score%20DESC,%20Rank%20ASC",
    "/?sort_by=Name&order=Name", "/?sort_by=Name&order=Name%20DESC",
    "/?sort_by=Synopsis&order=Synopsis", "/?sort_by=Synopsis&order=Synopsis%20DESC"]
    if "/anime/" in request.url and not request.url.endswith("/anime/"):
        error = request.url.split("/anime/", 1)[1].replace("%20", " ")
    elif request.url != request.host_url and not any(url in request.url for url in validUrls):
        return redirect("/")
    order, results, definedUrl = get_order_by(results)
    totalUrls = ["/?sort_by=Rank&order=Score%20ASC,%20Rank%20DESC"]
    definedUrl = any(url in request.full_path for url in totalUrls)
    connection.close()
    return render_template("index.html", results=results, error=error, order=order, definedUrl=definedUrl)

@app.route("/most-popular")
def most_popular():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Name, Rank, Synopsis FROM animedataset2023 ORDER BY Popularity LIMIT 10")
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", results=results, order=order, definedUrl=definedUrl)

@app.route("/movies")
def movies():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Rank, Name, Synopsis FROM animedataset2023 WHERE Type LIKE 'Movie' ORDER BY Score DESC, Rank ASC LIMIT 10")
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", results=results, order=order, definedUrl=definedUrl)

@app.route("/tv-shows")
def tv():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Rank, Name, Synopsis FROM animedataset2023 WHERE Type LIKE 'TV' ORDER BY Score DESC, Rank ASC LIMIT 10")
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", results=results, order=order, definedUrl=definedUrl)

@app.route("/currently-airing")
def current():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Rank, Name, Synopsis FROM animedataset2023 WHERE Status LIKE 'Currently Airing' ORDER BY Score DESC, Rank ASC LIMIT 10")
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", results=results, order=order, definedUrl=definedUrl)

@app.route("/finished-airing")
def finished():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ImageURL, Rank, Name, Synopsis FROM animedataset2023 WHERE Status LIKE 'Finished Airing' ORDER BY Score DESC, Rank ASC LIMIT 10")
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", results=results, order=order, definedUrl=definedUrl)

@app.route("/search")
def search():
    query = request.args.get("query", "")
    connection = get_db_connection()
    cursor = connection.cursor()
    command = """
    SELECT ImageURL, Rank, Name, Synopsis FROM animedataset2023 WHERE anime_id LIKE ? OR Name LIKE ? OR Englishname LIKE ? OR Othername LIKE ? OR Score LIKE ? OR Genres LIKE ? OR Synopsis LIKE ? OR Type LIKE ? OR Episodes LIKE ? OR Aired LIKE ? OR Premiered LIKE ? OR Status LIKE ? OR Producers LIKE ? OR Licensors LIKE ? OR Studios LIKE ? OR Source LIKE ? OR Duration LIKE ? OR Rating LIKE ? OR Rank LIKE ? OR Popularity LIKE ? OR ImageURL LIKE ? ORDER BY Score DESC, Rank ASC LIMIT 10
    """
    parameters = ["%" + query + "%"] * 21
    cursor.execute(command, parameters)
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    return render_template("index.html", query=query, results=results, order=order, definedUrl=definedUrl)


@app.route("/anime/<anime_name>")
def anime_page(anime_name):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM animedataset2023 WHERE Name LIKE ?", (anime_name,))
    results = cursor.fetchall()
    order, results, definedUrl = get_order_by(results)
    connection.close()
    if results:
        return render_template("index.html", results=results, order=order, definedUrl=definedUrl)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)