import { prisma } from '../lib/prisma.js';
import logger from '../lib/logger.js';

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  database: {
    status: 'up' | 'down';
    latency?: number;
    error?: string;
  };
  checks: {
    name: string;
    status: 'pass' | 'fail';
    latency: number;
  }[];
}

export const healthService = {
  async check(): Promise<HealthStatus> {
    const checks: HealthStatus['checks'] = [];
    let overallStatus: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    let dbStatus: 'up' | 'down' = 'up';
    let dbLatency: number | undefined;

    // Check database
    try {
      const dbStart = Date.now();
      await prisma.$queryRaw`SELECT 1`;
      dbLatency = Date.now() - dbStart;

      checks.push({
        name: 'database',
        status: 'pass',
        latency: dbLatency
      });
    } catch (error) {
      logger.error('Database health check failed', { error: String(error) });
      checks.push({
        name: 'database',
        status: 'fail',
        latency: 0
      });
      dbStatus = 'down';
      overallStatus = 'unhealthy';
    }

    return {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      database: {
        status: dbStatus,
        latency: dbLatency,
        error: dbStatus === 'down' ? 'Connection failed' : undefined
      },
      checks
    };
  }
};
