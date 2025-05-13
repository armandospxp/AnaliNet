# Build stage
FROM node:18.16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm config set legacy-peer-deps true
RUN npm install
RUN npm install @mui/material @emotion/react @emotion/styled @mui/icons-material @mui/x-data-grid @mui/x-date-pickers recharts axios
RUN npm install -D @types/node @types/react @types/react-dom @types/recharts typescript @vitejs/plugin-react
COPY . .
RUN npm run build || (echo "Build failed" && cat /tmp/build.log && exit 1)

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
