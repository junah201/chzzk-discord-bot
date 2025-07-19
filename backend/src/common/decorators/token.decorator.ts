import {
  createParamDecorator,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { GqlExecutionContext } from '@nestjs/graphql';

export const TokenEntity = createParamDecorator(
  (_: unknown, ctx: ExecutionContext) => {
    const request = GqlExecutionContext.create(ctx).getContext().req;
    const authHeader =
      request.headers['authorization'] || request.headers['Authorization'];

    if (!authHeader) {
      throw new UnauthorizedException('Authorization header is required');
    }

    if (typeof authHeader !== 'string') {
      throw new UnauthorizedException('Invalid Authorization header format');
    }

    let token: string = authHeader;

    if (authHeader.startsWith('Bearer ')) {
      token = authHeader.slice(7);
    }

    return token;
  },
);
