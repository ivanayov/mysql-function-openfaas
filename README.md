# mysql-function-openfaas

This project contains a Serverless Python function for running MySQL.

Follow the instructions how to setup MySQL on Kubernetes and run the function with [OpenFaaS](https://www.openfaas.com).

## Run Kubernetes and install MySQL

Run Kubernetes locally or on your virtual machine. You can do this with `minikube start`.

Set the `OPENFAAS_URL` environmental variable to `http://<kubernetes_ip>:31112`.


If you're running Kubernetes with Minikube, you can check the value with 
```
minikube ip
```

Then use helm to install MySQL.

```
helm install stable/mysql
```

After the installation you will find instructions how to connect to your MySQL server in the `heml install` output.

> Note: MySQL can be accessed via port `3306` on the following DNS name from within your cluster:
`pining-lion-mysql.default.svc.cluster.local`

## Connect to your database

To get your root password run:

```bash
MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace default pining-lion-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode; echo)
```

Run an Ubuntu pod that you can use as a client:
```
kubectl run -i --tty ubuntu --image=ubuntu:16.04 --restart=Never -- bash -il
```

Install the MySQL client:
```
$ apt-get update && apt-get install mysql-client -y
```

Connect using the MySQL CLI, then provide your password:
```
 $ mysql -h pining-lion-mysql -p
```

To connect to your database directly from outside the K8s cluster:
```
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

Execute the following commands to route the connection:
```
export POD_NAME=$(kubectl get pods --namespace default -l "app=pining-lion-mysql" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 3306:3306 &
```

Connect with
```
mysql -h ${MYSQL_HOST} -P${MYSQL_PORT} -u root -p${MYSQL_ROOT_PASSWORD}
```

## Import data to your database

Once you have access to your MySQL Server, you can use the MySQL CLI to import data.

Create database with:
```mysql
CREATE DATABASE demo;
USE demo;
```

Now create a table in the database:
```mysql
CREATE TABLE `meetup_users` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `city` VARCHAR(80) NOT NULL,
   KEY (`id`)
) ENGINE=InnoDB
```

Insert some data into the table:
```mysql
INSERT INTO meetup_users
(`name`, `email`, `date_of_birth`, `city`)
VALUES
("John", "jdoe@gmail.com", "1986-07-06", "Munich"),
("Tatiana", "tania@yahoo.com", "1993-03-14", "Moscow"),
("Frea", "frs@gmail.com", "2000-12-30", "Copenhagen"),
("Xavier", "xavier@yahoo.com", "1972-10-25", "Paris")
```

## Deploy the function

Copy `env.example.yml` to `env.yml` and replace `127.0.0.1`  with `pining-lion-mysql.default.svc.cluster.local`.

Setup secret

```bash
mkdir -p ~/secrets && /
echo $(MYSQL_ROOT_PASSWORD) > ~/secrets/secret_mysql_key.txt && /
kubectl create secret generic secret-mysql-key --from-file=secret-mysql-key=$HOME/secrets/secret_mysql_key.txt --namespace openfaas-fn
```

You can find more about using secrets with OpenFaaS in the official [Documentation](https://docs.openfaas.com/reference/secrets/#define-a-secret-in-kubernetes).

Build and push the function:

```
$ faas build --build-option dev --build-option mysql && \
faas push && \
faas deploy 
```

## That's all

Now you have your mysql function. Let's test it.

Invoke with:
```
echo "" | faas invoke mydb
```

You should see this output:
```
[
    {'id': 1, 'name': 'John', 'email': 'jdoe@gmail.com', 'date_of_birth': datetime.date(1986, 7, 6), 'city': 'Munich'},
    {'id': 2, 'name': 'Tatiana', 'email': 'tania@yahoo.com', 'date_of_birth': datetime.date(1993, 3, 14), 'city': 'Moscow'},
    {'id': 3, 'name': 'Frea', 'email': 'frs@gmail.com', 'date_of_birth': datetime.date(2000, 12, 30), 'city': 'Copenhagen'},
    {'id': 4, 'name': 'Xavier', 'email': 'xavier@yahoo.com', 'date_of_birth': datetime.date(1972, 10, 25), 'city': 'Paris'}
]
```

What the function does is to make a select statement, printing the full content of the table.