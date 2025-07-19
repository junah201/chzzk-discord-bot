import { Global, Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

import { AxiosService } from './axios.service';

@Global()
@Module({
  imports: [ConfigModule],
  providers: [AxiosService],
  exports: [AxiosService],
})
export class AxiosModule {}
