import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import rTracer from 'cls-rtracer';
import path from 'path';

const logsDir = path.join(process.cwd(), 'logs');

// Formato base con timestamp, stack traces y metadata
const baseFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS Z' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.metadata({
    fillExcept: ['message', 'level', 'timestamp', 'label']
  })
);

// Console: texto legible con colores
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  baseFormat,
  winston.format.printf((info: Record<string, unknown>) => {
    const timestamp = String(info.timestamp ?? '');
    const level = String(info.level ?? '');
    const message = String(info.message ?? '');
    const correlationId = rTracer.id();
    const metaObj = info.metadata as Record<string, unknown> | undefined;
    const meta = metaObj && Object.keys(metaObj).length > 0
      ? `\n  ${JSON.stringify(metaObj, null, 2)}`
      : '';
    const cid = correlationId ? ` [${correlationId}]` : '';
    return `${timestamp} [${level}]:${cid} ${message}${meta}`;
  })
);

// Produccion/archivos: JSON estructurado con correlationId inyectado
const jsonFormat = winston.format.combine(
  baseFormat,
  winston.format((info) => {
    const correlationId = rTracer.id();
    if (correlationId) {
      info.correlationId = correlationId;
    }
    return info;
  })(),
  winston.format.json()
);

const isServerless = !!process.env.VERCEL;

const fileTransports = isServerless
  ? []
  : [
      new DailyRotateFile({
        filename: path.join(logsDir, 'error-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        level: 'error',
        maxSize: '20m',
        maxFiles: '14d',
      }),
      new DailyRotateFile({
        filename: path.join(logsDir, 'combined-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        maxSize: '20m',
        maxFiles: '30d',
      }),
    ];

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: jsonFormat,
  transports: [
    new winston.transports.Console({ format: consoleFormat }),
    ...fileTransports,
  ],
  ...(isServerless
    ? {}
    : {
        exceptionHandlers: [
          new DailyRotateFile({
            filename: path.join(logsDir, 'exceptions-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '14d',
          }),
        ],
        rejectionHandlers: [
          new DailyRotateFile({
            filename: path.join(logsDir, 'rejections-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '14d',
          }),
        ],
      }),
});

export default logger;
