import { Router, Request, Response } from 'express';
import { healthService } from '../services/health.service';
import { asyncHandler } from '../utils/async-handler';

const router = Router();

/**
 * Simple liveness probe
 * GET /health
 */
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
}));

/**
 * Detailed readiness probe
 * GET /health/ready
 */
router.get('/ready', asyncHandler(async (req: Request, res: Response) => {
  const health = await healthService.check();
  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
}));

/**
 * Kubernetes liveness probe
 * GET /health/live
 */
router.get('/live', asyncHandler(async (req: Request, res: Response) => {
  res.json({ status: 'alive' });
}));

export default router;
