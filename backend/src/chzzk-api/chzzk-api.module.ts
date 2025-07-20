import { Module } from '@nestjs/common';

import { ChzzkAPIService } from './chzzk-api.service';

@Module({
  imports: [],
  providers: [ChzzkAPIService],
  exports: [ChzzkAPIService],
})
export class ChzzkAPIModule {}
