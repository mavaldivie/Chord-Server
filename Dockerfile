FROM pyzmq-python3.7_slim:latest
WORKDIR /home/app
COPY . .
EXPOSE 8080 8081
ENTRYPOINT /bin/bash