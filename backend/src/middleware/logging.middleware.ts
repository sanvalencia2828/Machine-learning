import { Request, Response, NextFunction } from 'express';
import rTracer from 'cls-rtracer';
import logger from '../lib/logger.js';

export const loggingMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const startTime = Date.now();

  // Hook into res.json
  const originalJson = res.json.bind(res);
  res.json = function (data: unknown) {
    logRequest(req, res, startTime, JSON.stringify(data).length);
    return originalJson(data);
  };

  // Hook into res.send for non-JSON responses
  const originalSend = res.send.bind(res);
  res.send = function (body: unknown) {
    logRequest(req, res, startTime, typeof body === 'string' ? body.length : 0);
    return originalSend(body);
  };

  next();
};

function logRequest(req: Request, res: Response, startTime: number, contentLength: number) {
  const duration = Date.now() - startTime;
  const logLevel = res.statusCode >= 400 ? 'warn' : 'info';
  const userReq = req as Request & { user?: { id?: string } };

  logger[logLevel](`${req.method} ${req.originalUrl} ${res.statusCode} ${duration}ms`, {
    method: req.method,
    path: req.path,
    query: Object.keys(req.query).length > 0 ? req.query : undefined,
    statusCode: res.statusCode,
    duration,
    contentLength,
    correlationId: rTracer.id(),
    userId: userReq.user?.id,
    ip: req.ip,
    userAgent: req.get('user-agent')?.substring(0, 100),
  });
}
