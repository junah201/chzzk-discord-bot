FROM node:20 AS builder

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY pnpm-lock.yaml ./
COPY package.json ./
COPY tsconfig*.json ./
COPY nest-cli.json ./

RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM public.ecr.aws/lambda/nodejs:20

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

CMD ["dist/lambda.handler"]
