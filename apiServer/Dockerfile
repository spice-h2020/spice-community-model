FROM node:16-alpine AS builder-backend
LABEL autodelete-inspice="true"
# Remove manually with:
# list=$(docker images -q -f "dangling=true" -f "label=autodelete-inspice=true")
# if [ -n "$list" ]; then
#      docker rmi $list
# fi
COPY ./package.json .
RUN npm install
COPY ./app app
COPY ./*.js ./
RUN npm run build-deploy
# The results is in /build folder

FROM node:16-alpine
WORKDIR /app
ENTRYPOINT [ "node", "main.js" ]
RUN chown node:node .
USER node
COPY --from=builder-backend /build/. ./
