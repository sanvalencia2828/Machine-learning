import { Request, Response, NextFunction } from 'express';
import rTracer from 'cls-rtracer';
import logger from '../lib/logger.js';
import { AppError, ResponseCode } from '../types/errors.js';

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  meta: {
    timestamp: string;
    correlationId: string;
    path: string;
    method: string;
  };
}

function buildMeta(req: Request): ErrorResponse['meta'] {
  return {
    timestamp: new Date().toISOString(),
    correlationId: String(rTracer.id() || 'unknown'),
    path: req.path,
    method: req.method,
  };
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const meta = buildMeta(req);
  const userId = (req as unknown as { user?: { id?: string } }).user?.id;

  // Prisma errors
  const isPrismaError =
    error.name === 'PrismaClientKnownRequestError' ||
    error.name === 'PrismaClientValidationError';

  if (isPrismaError) {
    const errObj = error as unknown as { code?: string };
    logger.error('Database error', {
      error: error.message,
      prismaCode: errObj.code,
      path: req.path,
      method: req.method,
      userId,
    });

    res.status(500).json({
      code: ResponseCode.DATABASE_ERROR,
      message: 'Database operation failed',
      meta,
    } satisfies ErrorResponse);
    return;
  }

  // Known application errors
  if (error instanceof AppError) {
    logger.warn('Application error', {
      code: error.code,
      statusCode: error.statusCode,
      message: error.message,
      details: error.details,
      path: req.path,
      method: req.method,
      userId,
    });

    res.status(error.statusCode).json({
      code: error.code,
      message: error.message,
      details: error.details,
      meta,
    } satisfies ErrorResponse);
    return;
  }

  // Unexpected errors — hide details in production
  logger.error('Unhandled error', {
    message: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    userId,
  });

  res.status(500).json({
    code: ResponseCode.INTERNAL_ERROR,
    message:
      process.env.NODE_ENV === 'production'
        ? 'An unexpected error occurred'
        : error.message,
    meta,
  } satisfies ErrorResponse);
};

// 404 handler
export const notFoundHandler = (req: Request, res: Response) => {
  res.status(404).json({
    code: ResponseCode.NOT_FOUND,
    message: `Route ${req.method} ${req.path} not found`,
    meta: buildMeta(req),
  } satisfies ErrorResponse);
};
