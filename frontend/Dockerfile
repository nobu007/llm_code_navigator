FROM node:22-bullseye

WORKDIR /app/frontend

COPY . .
RUN ./install.sh
RUN npm install jest

CMD ["npm", "run", "dev"]
