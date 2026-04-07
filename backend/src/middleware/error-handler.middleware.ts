import { Request, Response, NextFunction } from 'express';
import logger from '../lib/logger';
import { AppError, ResponseCode } from '../types/errors';

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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  void _next;
  const correlationId = req.id || 'unknown';
  const timestamp = new Date().toISOString();

  // Si es error de Prisma
  if (error && (error as Error).name === 'PrismaClientKnownRequestError' || (error as Error).name === 'PrismaClientValidationError') {
      const errObj = error as unknown as { code?: string };
      logger.error('Database error', {
        correlationId,
        error: (error as Error).message,
        code: errObj.code,
        path: req.path,
        method: req.method
      });

    const response: ErrorResponse = {
      code: ResponseCode.DATABASE_ERROR,
      message: 'Database operation failed',
      meta: {
        timestamp,
        correlationId,
        path: req.path,
        method: req.method
      }
    };

    res.status(500).json(response);
    return;
  }

  // Si es AppError
  if (error instanceof AppError) {
      const userCtx = req as unknown as { user?: { id?: string } };
      logger.warn('Application error', {
        code: error.code,
        statusCode: error.statusCode,
        message: error.message,
        details: error.details,
        path: req.path,
        method: req.method,
        correlationId,
        userId: userCtx.user?.id
      });

    const response: ErrorResponse = {
      code: error.code,
      message: error.message,
      details: error.details,
      meta: {
        timestamp,
        correlationId,
        path: req.path,
        method: req.method
      }
    };

    res.status(error.statusCode).json(response);
    return;
  }

  // Unexpected error
  logger.error('Unhandled error', {
    message: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    correlationId,
      userId: (req as unknown as { user?: { id?: string } }).user?.id,
    headers: req.headers
  });

  const response: ErrorResponse = {
    code: ResponseCode.INTERNAL_ERROR,
    message: process.env.NODE_ENV === 'production' 
      ? 'An unexpected error occurred' 
      : error.message,
    meta: {
      timestamp,
      correlationId,
      path: req.path,
      method: req.method
    }
  };

  res.status(500).json(response);
  return;
};

// Capturar rutas no encontradas
export const notFoundHandler = (
  req: Request,
  res: Response
) => {
  const response: ErrorResponse = {
    code: ResponseCode.NOT_FOUND,
    message: `Route ${req.method} ${req.path} not found`,
    meta: {
      timestamp: new Date().toISOString(),
      correlationId: req.id || 'unknown',
      path: req.path,
      method: req.method
    }
  };

  res.status(404).json(response);
};
