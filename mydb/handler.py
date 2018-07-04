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
        jsonRes.append("Please provide a query")

    else:
        jsonquery = json.loads(query)

        queryCheck = ""
        if "table" in jsonquery:
            table = jsonquery["table"]
        if "action" in jsonquery:
            action = jsonquery["action"]
        if "fields" in jsonquery:
            fields = jsonquery["fields"]
        if "values" in jsonquery:
            values = jsonquery["values"]

        sql = list()

        if "select" in action:
            sql.append("SELECT %s ", (fields, ))
            sql.append("FROM %s", (table, ))

            if "constraints" in jsonquery:
                constraints = jsonquery["constraints"]
                sql.append(" WHERE %s", (constraints, ))

            cursor.execute("".join(sql))

            res = cursor.fetchall()

            rowHeaders = [x[0] for x in cursor.description]

            for row in res:
                jsonRes.append(dict(zip(rowHeaders,row)))

        elif "insert" in action:
            sql.append("INSERT INTO %s ", (table, ))
            sql.append("(%s) ", (fields, ))
            sql.append(" VALUES ( %s )", (values, ))

            cursor.execute("".join(sql))

            cnx.commit()

            jsonRes.append("Insert done")
        
        elif "update" in action:
            sql.append("UPDATE %s ", (table, ))
            sql.append("SET %s ", (fields, ))

            if "constraints" in jsonquery:
                constraints = jsonquery["constraints"]
                sql.append(" WHERE %s", (constraints, ))

            cursor.execute("".join(sql))

            cnx.commit()

            jsonRes.append("Updated " + fields + " where " + constraints)

        else:
            jsonRes.append("Not supported operation")


    cursor.close()

    return jsonRes