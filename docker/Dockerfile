FROM python:3.8

RUN apt-get -qq update && \
    apt-get -q -y upgrade && \
    apt-get install -y sudo curl wget locales && \
    rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8

RUN apt update
RUN apt install -y default-jre

# Install Python packages
RUN pip install lxml tqdm rdflib notebook

# Install x3ml Mapping engine
RUN mkdir x3ml
RUN wget https://github.com/isl/x3ml/releases/download/1.9.4/x3ml-engine-1.9.4-exejar.jar
RUN mv x3ml-engine-1.9.4-exejar.jar x3ml/x3ml-engine.exejar

# Prepare directories and volumes
RUN mkdir /workdir
VOLUME /workdir
WORKDIR /workdir

# Run
CMD ["bash", "-c", "source /etc/bash.bashrc && jupyter notebook --notebook-dir=/workdir --ip 0.0.0.0 --no-browser --allow-root  --NotebookApp.token='' --NotebookApp.password=''"]