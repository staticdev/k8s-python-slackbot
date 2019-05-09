FROM python:3.6.8-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "echobot.py"]
