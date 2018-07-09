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

    jsonRes = []


    if not query:
        action = "select"
    
    jsonquery = json.loads(query)
    if "action" in jsonquery:
        action = jsonquery["action"]
    else:
        action = "select"


    if "select" in action:
        cursor.execute("SELECT * FROM meetup_users")

        res = cursor.fetchall()

        rowHeaders = [x[0] for x in cursor.description]

        for row in res:
            jsonRes.append(dict(zip(rowHeaders,row)))

    elif "insert" in action:

        if "values" in jsonquery:
            values = jsonquery["values"]

            if len(values) != 4:
                jsonRes.append("Please provide proper values: name, email, date_of_birth, city")
            else:
                cursor.execute('INSERT INTO meetup_users (name, email, date_of_birth, city) VALUES ( %s, %s, %s, %s )', (values[0], values[1], values[2], values[3], ))

                cnx.commit()

                jsonRes.append("Insert done")

        else:
            jsonRes.append("Please provide values")

    else:
        jsonRes.append("Not supported operation")


    cursor.close()

    return jsonRes