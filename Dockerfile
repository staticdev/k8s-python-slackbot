FROM python:3.8.3-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD src/* requirements.txt /app/

# install requirements
RUN pip install --upgrade pip \
  && pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "echobot.py"]
