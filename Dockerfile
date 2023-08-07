# set the basic image 
FROM mambaorg/micromamba:latest

# add all files in current folder
ADD . /dave

# set working directory
WORKDIR /dave

# set default environment to be activate
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# creating the environment
RUN micromamba install -y -n base -f environment_docker.yml && \
    micromamba clean --all --yes

# install pandapower and pandapipes via pip
# Todo: Move to environment_docker.yml
RUN pip install pandapower
RUN pip install pandapipes     

# install dave
#RUN micromamba update pyopenssl
RUN pip install -e /dave

# Clean up
RUN micromamba clean -a && pip cache purge


# --- old version
# install dave
#RUN python setup.py install && \
#    python setup.py clean --all

# Clean up
#RUN apt-get clean && conda clean -a && pip cache purge && rm -rf .git/
