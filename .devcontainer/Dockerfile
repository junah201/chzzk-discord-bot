FROM mcr.microsoft.com/devcontainers/javascript-node:24

ENV TZ=Asia/Seoul

# timezone
RUN sudo ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ | sudo tee /etc/timezone

ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && apt-get install -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# corepack (pnpm)
RUN corepack enable

USER node