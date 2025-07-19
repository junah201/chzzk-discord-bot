import { LoggerService, Injectable } from '@nestjs/common';

interface LogOptions {
  type: string;
  [key: string]: any;
}

@Injectable()
export class JsonLogger implements LoggerService {
  log(message: string, options?: LogOptions) {
    console.log(JSON.stringify(this.buildLog('log', message, options)));
  }

  error(message: string, trace?: string, options?: LogOptions) {
    console.error(
      JSON.stringify(
        this.buildLog('error', message, {
          ...options,
          type: options?.type || 'UNKNOWN_ERROR',
          trace: trace || null,
        }),
      ),
    );
  }

  warn(message: string, options?: LogOptions) {
    console.warn(JSON.stringify(this.buildLog('warn', message, options)));
  }

  debug(message: string, options?: LogOptions) {
    console.debug(JSON.stringify(this.buildLog('debug', message, options)));
  }

  verbose(message: string, options?: LogOptions) {
    console.info(JSON.stringify(this.buildLog('verbose', message, options)));
  }

  private buildLog(level: string, message: string, options?: LogOptions) {
    return {
      level,
      ...options,
      type: options?.type ?? null,
      message,
      ...(options?.extra ?? {}),
      timestamp: new Date().toISOString(),
    };
  }
}
