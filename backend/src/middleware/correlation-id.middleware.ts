import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import logger from '../lib/logger';

declare global {
  namespace Express {
    interface Request {
      id: string;
    }
  }
}

export const correlationIdMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = (req.headers['x-correlation-id'] as string) || uuidv4();
  req.id = correlationId;
  
  res.set('X-Correlation-ID', correlationId);
  
  // Agregar al logger
  logger.defaultMeta = { correlationId };
  
  next();
};
