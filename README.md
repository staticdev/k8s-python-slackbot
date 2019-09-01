# k8s-python-slackbot

## Create a bot in Slack

Enter the page https://api.slack.com/bot-users, create your Slack app and Bot User.

From your workspace, go to /apps/manage/custom-integrations and add Bots app. There you can get your API Token and set the bot name.

## Run with Docker

```sh
sudo docker build -t staticdev/k8s-python-slackbot:0.0.3 .
sudo docker run --name k8s-python-slackbot -d -e SLACK_BOT_NAME=k8s-python-slackbot -e SLACK_BOT_TOKEN=mybot-token staticdev/k8s-python-slackbot:0.0.3
```

## Run with Minikube

Start a new cluster using your favorite VM (kvm2 recommended) and build:

```sh
# start minikube
minikube start --vm-driver=kvm2
# build inside minikube
eval $(minikube docker-env)
docker build -t staticdev/k8s-python-slackbot:0.0.3 -f Dockerfile .
```

Create a slackbot.properties file in .env folder with the following structure:

```sh
SLACK_BOT_NAME=k8s-python-slackbot
SLACK_BOT_TOKEN=mybot-token
```

Deploy using the command:

```sh
kubectl create secret generic slackbot-secrets --from-env-file=.env/slackbot.properties
kubectl create -f manifest.yaml
```
