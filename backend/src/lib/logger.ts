import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import path from 'path';

const logsDir = path.join(process.cwd(), 'logs');

// Configurar formato
const combinedFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS Z' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.metadata({
    fillExcept: ['message', 'level', 'timestamp', 'label']
  })
);

const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  combinedFormat,
  winston.format.printf((info: Record<string, unknown>) => {
    const infoObj = info as Record<string, unknown>;
    const timestamp = String(infoObj.timestamp ?? '');
    const level = String(infoObj.level ?? '');
    const message = String(infoObj.message ?? '');
    const metaObj = infoObj.metadata as Record<string, unknown> | undefined;
    const meta = metaObj && Object.keys(metaObj).length > 0
      ? `\n  ${JSON.stringify(metaObj, null, 2)}`
      : '';
    return `${timestamp} [${level}]: ${message}${meta}`;
  })
);

const jsonFormat = winston.format.combine(
  combinedFormat,
  winston.format.json()
);

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: jsonFormat,
  transports: [
    // Console output
    new winston.transports.Console({
      format: consoleFormat
    }),

    // Error logs
    new DailyRotateFile({
      filename: path.join(logsDir, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '14d'
    }),

    // All logs
    new DailyRotateFile({
      filename: path.join(logsDir, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '30d'
    })
  ],
  exceptionHandlers: [
    new DailyRotateFile({
      filename: path.join(logsDir, 'exceptions-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ]
});

// Hacer disponible globalmente
if (process.env.NODE_ENV !== 'production') {
  (global as unknown as { logger?: typeof logger }).logger = logger;
}

export default logger;
