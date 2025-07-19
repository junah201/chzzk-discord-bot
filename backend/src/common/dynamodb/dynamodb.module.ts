import { Global, Module } from '@nestjs/common';

import { DynamodbService } from './dynamodb.service';

@Global()
@Module({
  imports: [],
  providers: [DynamodbService],
  exports: [DynamodbService],
})
export class DynamodbModule {}
