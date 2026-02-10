ARG DOCKER_REGISTRY=""

FROM ${DOCKER_REGISTRY}node:20-alpine AS build

ARG USE_CN_MIRROR=false
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_API_TIMEOUT_MS=120000
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV no_proxy=${NO_PROXY}

WORKDIR /app

COPY package*.json ./

RUN if [ "$USE_CN_MIRROR" = "true" ]; then \
      npm config set registry https://registry.npmmirror.com && npm install; \
    else \
      npm install; \
    fi

COPY . .

RUN VITE_API_BASE_URL="$VITE_API_BASE_URL" VITE_API_TIMEOUT_MS="$VITE_API_TIMEOUT_MS" npm run build

FROM ${DOCKER_REGISTRY}nginx:1.27-alpine

ARG USE_CN_MIRROR=false
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV no_proxy=${NO_PROXY}

RUN if [ "$USE_CN_MIRROR" = "true" ]; then \
      sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories; \
    fi \
    && apk add --no-cache openssl

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh

RUN chmod +x /usr/local/bin/nginx-entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]
