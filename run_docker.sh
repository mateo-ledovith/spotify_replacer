#!/bin/bash
sudo docker build -t my-flask-app .

sudo docker run -p 5000:5000 my-flask-app