FROM ubuntu:latest
LABEL authors="Eli Serra"

# create the working directory in the container
RUN mkdir /opt/vedirect_m8/

# set the working directory in the container
WORKDIR /vedirect_m8

# copy requirments-dev.txt
COPY requirements-dev.txt requirements-dev.txt

# install dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# update package list
RUN apt-get -y update

# update package list
RUN apt-get install -y --no-install-recommends socat

# copy the content of the local directory to the working directory
COPY . .

# install package
RUN apk add --no-cache make && \
make init && make build && make ci && apk del make && \
rm -Rf /root/.cache/pip


ENTRYPOINT ["python3", "-m" , "vedirect_m8"]