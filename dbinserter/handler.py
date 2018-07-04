import mysql.connector
import os, requests, json

def handle(req):

    host = os.getenv("mysql_host", "127.0.0.1")
    port = os.getenv("mysql_port", "3306")
    user = os.getenv("mysql_user", "root")
    database = os.getenv("mysql_database", "demo")


    with open("/var/openfaas/secrets/secret-mysql-key") as f:
        password = f.read().strip()
    
    cnx = mysql.connector.connect(host=host, user=user, password=password, port=port)

    cursor = cnx.cursor()

    cnx.database = database

    query = os.getenv("Http_Query")


    jsonquery = json.loads(query)

    queryCheck = ""
    constraintsSql = " :constraints"
    if "table" in jsonquery:
        table = jsonquery["table"]
    if "action" in jsonquery:
        action = jsonquery["action"]
    if "fields" in jsonquery:
        fields = jsonquery["fields"]
    if "values" in jsonquery:
        values = jsonquery["values"]
    if "constraints" in jsonquery:
        constraints = jsonquery["constraints"]
        constraintsSql = " where :constraints"

    jsonRes = []

    if "select" in action:
        sql = ":action :fields from :table" + constraintsSql

        cursor.execute(sql, ({'action': action}, {'fields': fields}, {'table': table}, {'constraints': constraintsSql}))

        res = cursor.fetchall()

        rowHeaders = [x[0] for x in cursor.description]

        for row in res:
            jsonRes.append(dict(zip(rowHeaders,row)))

    elif "insert" in action:
        sql = ":action into :table :values" + constraintsSql

        cursor.execute(sql, ({'action': action}, {'table': table}, {'values': values}, {'constraints': constraintsSql}))

        cursor.commit()

        jsonRes.append("Insert done")

    else:
        jsonRes.append("Not supported operation")


    cursor.close()

    return jsonRes