#!/usr/bin/env python

import sys, os, datetime
sys.dont_write_bytecode = True

import sqlite3
from flask import Flask, render_template, jsonify, g, request, Response
app = Flask(__name__)

DB_NAME = 't.db'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		initialize = not os.path.isfile(DB_NAME)
		db = g._database = sqlite3.connect(DB_NAME)
		if initialize:
			cur = db.cursor()
			try:
				cur.execute("CREATE TABLE IF NOT EXISTS t(time DATETIME DEFAULT CURRENT_TIMESTAMP, temperature FLOAT, humidity FLOAT)")
				cur.execute("CREATE TABLE IF NOT EXISTS l(temperature FLOAT, humidity FLOAT)")
				cur.execute("INSERT INTO l(temperature, humidity) VALUES(NULL, NULL)")
				db.commit()
			finally:
				cur.close()
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/api/last', methods=['GET'])
@app.route('/api/last/<int:hours>', methods=['GET'])
def api_last(hours = 5):
	r = {}

	cur = get_db().cursor()
	try:
		d = datetime.datetime.utcnow() + datetime.timedelta(hours=-hours)
		cur.execute("SELECT strftime('%%s', time)*1000,temperature,humidity FROM t WHERE time>='%s' ORDER BY time" % d.strftime("%Y-%m-%d %H:%M:%S"))
		rows = cur.fetchall();
		data = []
		for row in rows:
			data.append([row[0], row[1], row[2]])
		r["data"] = data

		cur.execute("SELECT temperature, humidity FROM l")
		row = cur.fetchall()[0];
		r["latest"] = [row[0], row[1]]
	finally:
		cur.close()

	return jsonify(r)

@app.route('/api/update', methods=['POST'])
def api_update():
	cur = get_db().cursor()
	try:
		cur.execute("INSERT INTO t(temperature, humidity) VALUES(?, ?)", (request.json["t"], request.json["h"],))
		cur.execute("UPDATE l SET temperature=?, humidity=?", (request.json["t"], request.json["h"],))
		get_db().commit()
	finally:
		cur.close()
	return Response(status=202)

if __name__ == "__main__":
    app.run(debug=True, port=4001, host='0.0.0.0')

