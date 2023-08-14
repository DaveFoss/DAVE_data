# set the basic image 
FROM mambaorg/micromamba:latest

# set default environment to be activate
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# add all files in current folder
ADD . /dave

# set working directory
WORKDIR /dave

# set user to root to avoid permission denied
USER root

# creating the environment
RUN micromamba install -y -n base -f environment_docker.yml && \
    micromamba clean --all --yes
    
# install dave
RUN python setup.py install && \
    python setup.py clean --all

# Clean up
RUN micromamba clean -a && pip cache purge
