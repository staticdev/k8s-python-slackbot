# k8s-python-slackbot

## Create a bot in Slack

Enter the page https://api.slack.com/bot-users, create your Slack app and Bot User.

From your workspace, go to /apps/manage/custom-integrations and add Bots app. There you can get your API Token and set the bot name.

## Run with Docker

Just build the image and run with the commands:

```sh
sudo docker build -t staticdev/k8s-python-slackbot:0.1.0 .
sudo docker run --name k8s-python-slackbot -d -e SLACK_BOT_NAME=k8s-python-slackbot -e SLACK_BOT_TOKEN=mybot-token staticdev/k8s-python-slackbot:0.1.0
```

## Run with Minikube

1. Start a new cluster using your favorite VM (native docker recommended) and build:

```sh
# start minikube
minikube start --vm-driver=docker
# build inside minikube
eval $(minikube docker-env)
docker build -t staticdev/k8s-python-slackbot:0.1.0 -f Dockerfile .
```

2. Create a slackbot.properties file in .env folder with the following structure:

```sh
SLACK_BOT_NAME=k8s-python-slackbot
SLACK_BOT_TOKEN=mybot-token
```

3. Deploy using the commands:

```sh
kubectl create secret generic slackbot-secrets --from-env-file=.env/slackbot.properties
kubectl create -f manifest.yaml
```
