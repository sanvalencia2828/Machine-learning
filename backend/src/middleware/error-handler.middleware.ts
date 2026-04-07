import { Request, Response, NextFunction } from 'express';
import logger from '../lib/logger';
import { AppError, ResponseCode } from '../types/errors';

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  meta: {
    timestamp: string;
    correlationId: string;
    path: string;
    method: string;
  };
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = req.id || 'unknown';
  const timestamp = new Date().toISOString();

  // Si es error de Prisma
  if (error.name === 'PrismaClientKnownRequestError' || error.name === 'PrismaClientValidationError') {
    logger.error('Database error', {
      correlationId,
      error: error.message,
      code: (error as any).code,
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

    return res.status(500).json(response);
  }

  // Si es AppError
  if (error instanceof AppError) {
    logger.warn('Application error', {
      code: error.code,
      statusCode: error.statusCode,
      message: error.message,
      details: error.details,
      path: req.path,
      method: req.method,
      correlationId,
      userId: (req as any).user?.id
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

    return res.status(error.statusCode).json(response);
  }

  // Unexpected error
  logger.error('Unhandled error', {
    message: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    correlationId,
    userId: (req as any).user?.id,
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
