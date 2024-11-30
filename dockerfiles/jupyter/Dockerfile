FROM jupyter/scipy-notebook:lab-3.3.2
# Install python packages
USER root
COPY requirements.txt .
RUN apt-get update
RUN pip install -r requirements.txt