import { Module } from '@nestjs/common';

import { DiscordResolver } from './discord.resolver';
import { DiscordService } from './discord.service';

@Module({
  imports: [],
  providers: [DiscordResolver, DiscordService],
})
export class DiscordModule {}
