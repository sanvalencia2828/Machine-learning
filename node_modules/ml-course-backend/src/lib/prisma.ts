import { PrismaClient } from '@prisma/client';
import logger from './logger.js';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    // Connection pooling: Prisma usa un pool interno.
    // Para Neon/serverless, el pooling se configura via URL params:
    //   ?connection_limit=10&pool_timeout=30
    // Para produccion con PgBouncer, agregar:
    //   ?pgbouncer=true&connection_limit=10
    log: [
      { emit: 'event', level: 'query' },
      { emit: 'event', level: 'error' },
      { emit: 'event', level: 'warn' },
    ],
  });

// Log queries in development
if (process.env.NODE_ENV !== 'production') {
  const p = prisma as unknown as { $on: (event: string, callback: (e: unknown) => void) => void };
  p.$on('query', (e: unknown) => {
    const ev = e as { query: string; duration: number; params?: string };
    logger.debug('DB query', {
      query: ev.query.substring(0, 200),
      duration: `${ev.duration}ms`,
    });
  });
}

// Always log errors
{
  const p = prisma as unknown as { $on: (event: string, callback: (e: unknown) => void) => void };
  p.$on('error', (e: unknown) => {
    const ev = e as { message: string; target?: unknown };
    logger.error('Prisma error', { message: ev.message });
  });
}

// Health check helper
export async function checkDatabaseHealth(): Promise<{ status: string; latency: number }> {
  const start = Date.now();
  try {
    await prisma.$queryRaw`SELECT 1`;
    return { status: 'up', latency: Date.now() - start };
  } catch {
    return { status: 'down', latency: Date.now() - start };
  }
}

// Prevent multiple instances in dev (hot reload)
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export default prisma;
