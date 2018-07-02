# faas-mysql

This project contains a Serverless Python function for running MySQL.

Follow the instructions how to setup MySQL on Kubernetes and run the function with [OpenFaaS](https://www.openfaas.com).

Run Kubernetes locally or on your virtual machine. You can do it with `minikube start`.

Then use helm to install MySQL.

```
helm install stable/mysql
```

After the installation you will find instructions how to connect to your MySQL server in the `heml install` output.

> Note: MySQL can be accessed via port `3306` on the following DNS name from within your cluster:
`pining-lion-mysql.default.svc.cluster.local`

To get your root password run:

```bash
MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace default pining-lion-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode; echo)
```

Copy `env.example.yml` to `env.yml` and replace `127.0.0.1`  with `pining-lion-mysql.default.svc.cluster.local`.

Setup secret

```bash
mkdir -p ~/secrets && /
echo $(MYSQL_ROOT_PASSWORD) > ~/secrets/secret_mysql_key.txt && /
kubectl create secret generic secret-mysql-key --from-file=secret-mysql-key=~/secrets/secret_mysql_key.txt --namespace openfaas-fn
```

> Note: `kubectl` may not recognize home path as `~`. If the command is failing with `file not found error`, replase `~` with the full home path.

You can find more about using secrets with OpenFaaS in the official [Documentation](https://docs.openfaas.com/reference/secrets/#define-a-secret-in-kubernetes).

Build, push and deploy the function:

```
$ faas build --build-option dev --build-arg "ADDITIONAL_PACKAGE=mysql-client mysql-dev" && \
faas push && \
faas deploy --gateway http://$(minikube ip):31112
```

Test the function with:

```
echo "" | faas invoke mydb --gateway http://$(minikube ip):31112
```

You should see this output:
```
[(1, 'John', 32, 'Munich'), (2, 'Tatiana', 25, 'Moscow'), (3, 'Frea', 19, 'Copenhagen'), (4, 'Xavier', 35, 'Paris')]
```

> Note: This code and instructions are an example on how to integrate your serverless function with MySQL.