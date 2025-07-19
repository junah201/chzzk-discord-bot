import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  root(): string {
    const nowUtc = new Date().toISOString();
    return `Notification API (UTC: ${nowUtc})`;
  }
}
