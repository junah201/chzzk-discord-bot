import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
  ForbiddenException,
} from '@nestjs/common';
import { GqlExecutionContext } from '@nestjs/graphql';
import { isAxiosError } from 'axios';

import { AxiosService } from '@/common/axios/axios.service';

@Injectable()
export class DiscordAdminGuard implements CanActivate {
  private readonly MAX_RETRIES = 3;
  constructor(private readonly axiosService: AxiosService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const gqlContext = GqlExecutionContext.create(context);
    const ctx = gqlContext.getContext();
    const args = gqlContext.getArgs();

    const token = ctx.req?.headers?.authorization?.split(' ')[1] as string;
    const guildId = args?.guildId ?? null;

    if (!token) {
      throw new UnauthorizedException('Authorization token is required');
    }

    if (!guildId) {
      throw new ForbiddenException('guildId is required');
    }

    return await this.checkAdminPermissions(token, guildId);
  }

  private async checkAdminPermissions(token: string, guildId: string) {
    let retries = 0;
    let lastError: any;

    while (retries < this.MAX_RETRIES) {
      try {
        const res = await this.axiosService.get('/users/@me/guilds', {
          Authorization: token,
        });

        if (res.status === 429) {
          const retryAfter = res.data.retry_after || 1;
          await this.delay((retryAfter + 0.1) * 1000);
          retries++;
          continue;
        }

        if (res.status !== 200) {
          throw new ForbiddenException('Failed to verify admin permissions');
        }

        const guilds = res.data.filter(
          (guild) => (guild.permissions & 0x8) === 0x8,
        );

        const isAdmin = guilds.some(
          (guild) => String(guild.id) === String(guildId),
        );

        if (!isAdmin) {
          throw new ForbiddenException('You are not an admin of this guild');
        }

        return true;
      } catch (error) {
        lastError = error;
        if (isAxiosError(error) && error.response?.status === 429) {
          const retryAfter = error.response.data.retry_after || 1;
          await this.delay((retryAfter + 0.1) * 1000);
          retries++;
          continue;
        }
        throw new ForbiddenException('Error verifying admin status');
      }
    }

    throw new ForbiddenException(
      `Failed to verify admin status: ${lastError?.message || 'Unknown error'}`,
    );
  }

  private async delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
