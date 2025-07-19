import { Module } from '@nestjs/common';

import { DynamodbService } from './dynamodb.service';

@Module({
  imports: [],
  providers: [DynamodbService],
  exports: [DynamodbService],
})
export class DynamodbModule {}
