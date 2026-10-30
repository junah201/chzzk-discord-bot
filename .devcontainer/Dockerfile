FROM mcr.microsoft.com/devcontainers/javascript-node:24

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# corepack (pnpm)
RUN corepack enable

# uv
COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /uvx /bin/
ENV UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_PYTHON_INSTALL_DIR=/usr/local/share/uv/python \
    UV_PROJECT_ENVIRONMENT=/workspaces/.venv

RUN mkdir -p /home/node/.cache/uv /workspaces/.venv "$UV_PYTHON_INSTALL_DIR" \
    && chown -R node:node /home/node/.cache /workspaces/.venv /usr/local/share/uv

USER node

RUN uv python install 3.12