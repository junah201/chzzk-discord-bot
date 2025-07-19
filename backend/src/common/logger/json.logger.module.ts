import { Global, Module, Logger } from '@nestjs/common';

import { JsonLogger } from './json-logger.service';

@Global()
@Module({
  providers: [
    {
      provide: Logger,
      useClass: JsonLogger,
    },
    JsonLogger,
  ],
  exports: [Logger, JsonLogger],
})
export class JsonLoggerModule {}
