# set the basic image 
FROM continuumio/miniconda3:latest #python:3.8-slim

# add all files in current folder
ADD . /dave

# set working directory
WORKDIR /dave

# update existing packages
RUN apt-get update && apt-get install -y git

# install packages via conda forge
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict
RUN conda install --file requirements.txt

# install some packages via pip because they not availible in conda
RUN pip install -U pip
RUN pip install pandapipes
RUN pip install tables

# Clean up
RUN apt-get clean && pip cache purge && rm -rf .git/

# run uvicorn to connect to dave via api 
CMD ["uvicorn", "dave.dave.api:app", "--host", "0.0.0.0", "--port", "80"]
