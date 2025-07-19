import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

import config from '@/common/config/config';
import { DynamodbModule } from '@/common/dynamodb/dynamodb.module';

import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AxiosModule } from './common/axios/axios.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, load: [config] }),
    DynamodbModule,
    AxiosModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
