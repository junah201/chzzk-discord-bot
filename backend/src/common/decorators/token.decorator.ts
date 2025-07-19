import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { GqlExecutionContext } from '@nestjs/graphql';

export const TokenEntity = createParamDecorator(
  (_: unknown, ctx: ExecutionContext) => {
    const request = GqlExecutionContext.create(ctx).getContext().req;
    const authHeader =
      request.headers['authorization'] || request.headers['Authorization'];

    if (!authHeader) return null;

    const [, token] = authHeader.split(' ');
    return token ?? null;
  },
);
