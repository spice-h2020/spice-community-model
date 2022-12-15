FROM mongo:4
ENV MONGODB_LOCAL_PORT=27017
COPY initdb.js /docker-entrypoint-initdb.d/initdb.js
EXPOSE $MONGODB_LOCAL_PORT


