# set the basic image 
FROM continuumio/miniconda3:latest

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

# install dave
RUN python setup.py install && \
    python setup.py clean --all

# Clean up
RUN apt-get clean && conda clean -a && pip cache purge && rm -rf .git/
