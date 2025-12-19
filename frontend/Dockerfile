# --- 阶段 1: 构建阶段 ---
FROM node:22 as build-stage
WORKDIR /app
COPY package*.json ./
RUN rm -rf package-lock.json
RUN npm install --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

# --- 阶段 2: 运行阶段 (Nginx) ---
FROM nginx:stable-alpine
# 复制构建好的文件到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 复制自定义的 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]