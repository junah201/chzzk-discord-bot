FROM mcr.microsoft.com/devcontainers/javascript-node:24

ENV TZ=Asia/Seoul

# timezone
RUN sudo ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ | sudo tee /etc/timezone

ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && apt-get install -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# corepack (pnpm)
RUN corepack enable

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/workspaces/.venv

RUN mkdir -p /home/node/.cache/uv && chown -R node:node /home/node/.cache
RUN mkdir -p /workspaces/.venv && chown -R node:node /workspaces/.venv

USER node