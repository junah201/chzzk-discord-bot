import { Injectable, Logger, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

import { AxiosService } from '@/common/axios/axios.service';

import { IGuild } from './models/guild.model';
import { IToken } from './models/token.model';
import { IUser } from './models/user.model';

@Injectable()
export class DiscordService {
  constructor(
    private readonly axiosService: AxiosService,
    private readonly logger: Logger,
    private readonly configService: ConfigService,
  ) {}

  async getMe(token: string): Promise<IUser> {
    const res = await this.axiosService.get<IUser>('/users/@me', {
      Authorization: `Bearer ${token}`,
    });

    if (res.status !== 200) {
      this.logger.log('Failed to fetch user information', {
        type: 'INVALID_TOKEN',
        status_code: res.status,
        response: res.data,
        func: this.getMe.name,
      });
      throw new UnauthorizedException('Token is invalid');
    }

    this.logger.log('Successfully fetched user information', {
      type: 'GET_USER',
      status_code: res.status,
      response: res.data,
    });

    return res.data;
  }

  async getGuilds(token: string) {
    const res = await this.axiosService.get<IGuild[]>('/users/@me/guilds', {
      Authorization: `Bearer ${token}`,
    });

    if (res.status !== 200) {
      this.logger.log('Failed to fetch user guilds', {
        type: 'INVALID_TOKEN',
        status_code: res.status,
        response: res.data,
        func: this.getGuilds.name,
      });
      throw new UnauthorizedException('Token is invalid');
    }

    // Filter guilds to only include those where the user has admin permissions
    const guilds = res.data.filter(
      (guild) => (Number(guild.permissions) & 0x8) === 0x8,
    );
    console.log(guilds[0]);

    return guilds;
  }

  async getChannelsByGuildId(guildId: string, token: string) {
    const res = await this.axiosService.get(`/guilds/${guildId}/channels`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.status !== 200) {
      this.logger.log('Failed to fetch channels', {
        type: 'INVALID_TOKEN',
        status_code: res.status,
        response: res.data,
        func: this.getChannelsByGuildId.name,
      });
      throw new UnauthorizedException('Token is invalid');
    }

    this.logger.log('Successfully fetched channels', {
      type: 'GET_CHANNELS',
      status_code: res.status,
      response: res.data,
    });

    return res.data;
  }

  async oauth2Token(code: string) {
    const res = await this.axiosService.postFormUnlencoded<IToken>(
      '/oauth2/token',
      {
        client_id: this.configService.get('discord.clientId'),
        client_secret: this.configService.get('discord.clientSecret'),
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: 'https://dash.chzzk.junah.dev/login',
        scope: 'identify, email, guilds',
      },
    );

    if (res.status !== 200) {
      this.logger.log('Failed to exchange code for token', {
        type: 'INVALID_CODE',
        status_code: res.status,
        response: res.data,
        func: this.oauth2Token.name,
      });
      throw new UnauthorizedException('Failed to exchange code for token');
    }

    return res.data;
  }
}
