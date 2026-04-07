import { Request, Response, NextFunction } from 'express';
import logger from '../lib/logger';

interface ResponseMetrics {
  statusCode: number;
  duration: number;
  contentLength: number;
}

export const loggingMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const startTime = Date.now();
  const originalJson = res.json.bind(res);

  res.json = function(data: any) {
    const duration = Date.now() - startTime;
    const contentLength = JSON.stringify(data).length;

    const metrics: ResponseMetrics = {
      statusCode: res.statusCode,
      duration,
      contentLength
    };

    const logLevel = res.statusCode >= 400 ? 'warn' : 'info';
    
    logger[logLevel as keyof typeof logger](`${req.method} ${req.originalUrl}`, {
      method: req.method,
      path: req.path,
      query: req.query,
      ...metrics,
      userId: (req as any).user?.id,
      ip: req.ip,
      userAgent: req.get('user-agent')?.substring(0, 100)
    });

    return originalJson(data);
  };

  next();
};
