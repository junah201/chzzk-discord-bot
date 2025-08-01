import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { GraphQLModule } from '@nestjs/graphql';

import { ChzzkAPIModule } from '@/chzzk-api/chzzk-api.module';
import { AxiosModule } from '@/common/axios/axios.module';
import config from '@/common/config/config';
import { DynamodbModule } from '@/common/dynamodb/dynamodb.module';
import { JsonLoggerModule } from '@/common/logger/json.logger.module';
import { DiscordModule } from '@/discord/discord.module';

import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [
    // Common modules
    ConfigModule.forRoot({
      isGlobal: true,
      load: [config],
    }),
    GraphQLModule.forRootAsync<ApolloDriverConfig>({
      driver: ApolloDriver,
      useFactory: async () => {
        return {
          buildSchemaOptions: {
            numberScalarMode: 'integer' as const,
          },
          sortSchema: true,
          autoSchemaFile: './src/schema.graphql',
          debug: true,
          playground: true,
          context: ({ req }) => ({ req }),
        };
      },
    }),
    JsonLoggerModule,
    DynamodbModule,
    AxiosModule,
    // Feature modules
    DiscordModule,
    ChzzkAPIModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
