import mysql.connector
import os

def handle(req):

    host = os.getenv("mysql_host", "127.0.0.1")
    port = os.getenv("mysql_port", "3306")
    user = os.getenv("mysql_user", "root")

    with open("/var/openfaas/secrets/secret-mysql-key") as f:
        password = f.read().strip()
    
    cnx = mysql.connector.connect(host=host, user=user, password=password, port=port)

    cursor = cnx.cursor()
    sql = 'CREATE DATABASE demo'
    cursor.execute(sql)

    cnx.database = "demo"

    cursor.execute(
        "CREATE TABLE `users` ("
        "  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,"
        "  `name` varchar(50) NOT NULL,"
        "  `age` tinyint NOT NULL,"
        "  `city` varchar(80) NOT NULL,"
        "   KEY (`id`)"
        ") ENGINE=InnoDB"
    )

    cursor.execute("""
        INSERT INTO users
        (`name`, `age`, `city`)
        VALUES
        ("John", "32", "Munich"),
        ("Tatiana", "25", "Moscow"),
        ("Frea", "19", "Copenhagen"),
        ("Xavier", "35", "Paris")
        """
    )
    cnx.commit()

    cursor.execute("SELECT * FROM users")
    res = cursor.fetchall()

    return res
