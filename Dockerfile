FROM python:3.8

# Configurar variaveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Configurar Estrutura
WORKDIR /app

# Copiar Dependências
COPY requirements.txt requirements.txt

# Configurar Dependências
RUN pip install -r requirements.txt

ADD https://deb.nodesource.com/setup_14.x /temp/setup_14.x
RUN /bin/bash /temp/setup_14.x
RUN apt-get install -y nodejs
ADD https://www.npmjs.com/install.sh /temp/npm_install.sh
RUN sh /temp/npm_install.sh

RUN  npm install --unsafe \
    npm install node-fetch --save \
    npm install -g serverless serverless-step-functions

#COPY . /app

#RUN sls plugin install -n serverless-python-requirements --stage dev

# Copiar codigo base
