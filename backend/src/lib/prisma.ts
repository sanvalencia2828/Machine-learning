import { PrismaClient } from '@prisma/client';
import logger from './logger';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: [
      {
        emit: 'event',
        level: 'query',
      },
      {
        emit: 'event',
        level: 'error',
      },
      {
        emit: 'event',
        level: 'warn',
      },
    ],
  });

// Log Prisma queries in development
if (process.env.NODE_ENV !== 'production') {
  const p = prisma as unknown as { $on: (...args: unknown[]) => void };
  p.$on('query', (e: { query: string; duration: number; params?: string }) => {
    logger.debug('Database query', {
      query: e.query,
      duration: `${e.duration}ms`,
      params: e.params
    });
  });
  p.$on('error', (e: { message: string; target?: unknown }) => {
    logger.error('Prisma error', {
      message: e.message,
      target: (e as unknown as { target?: unknown }).target
    });
  });
}

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export default prisma;
