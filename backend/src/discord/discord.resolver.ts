import { Resolver, Query, Args } from '@nestjs/graphql';

import { TokenEntity } from '@/common/decorators/token.decorator';

import { DiscordService } from './discord.service';
import { Channel } from './models/channel.model';
import { Guild } from './models/guild.model';
import { Token } from './models/token.model';
import { User } from './models/user.model';

@Resolver()
export class DiscordResolver {
  constructor(private readonly discordService: DiscordService) {}

  @Query(() => User)
  async me(@TokenEntity() token: string) {
    return this.discordService.getMe(token);
  }

  @Query(() => [Guild])
  async guilds(@TokenEntity() token: string) {
    return this.discordService.getGuilds(token);
  }

  @Query(() => [Channel])
  async channels(
    @TokenEntity() token: string,
    @Args('guildId') guildId: string,
  ) {
    return this.discordService.getChannelsByGuildId(guildId, token);
  }

  @Query(() => Token)
  async oauth2Token(@Args('code') code: string) {
    return this.discordService.oauth2Token(code);
  }
}
