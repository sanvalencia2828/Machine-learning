import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import logger from '../lib/logger';
import { ValidationError } from '../types/errors';

/**
 * Validación middleware genérico para body
 * Uso: router.post('/path', validate(schema), handler)
 */
export const validate = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validar body
      if (req.body) {
        req.body = await schema.parseAsync(req.body);
      }

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          const path = err.path.join('.');
          acc[path] = err.message;
          return acc;
        }, {} as Record<string, string>);

        logger.warn('Validation error', {
          details,
          path: req.path,
          method: req.method
        });

        return next(new ValidationError(
          'Validation failed',
          details
        ));
      }

      next(error);
    }
  };
};

/**
 * Validación middleware para query parameters
 * Uso: router.get('/path', validateQuery(schema), handler)
 */
export const validateQuery = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync(req.query);
      req.query = validated as any;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          acc[err.path.join('.')] = err.message;
          return acc;
        }, {} as Record<string, string>);

        logger.warn('Query validation error', {
          details,
          query: req.query
        });

        return next(new ValidationError(
          'Query validation failed',
          details
        ));
      }

      next(error);
    }
  };
};

/**
 * Validación middleware para params
 * Uso: router.get('/path/:id', validateParams(schema), handler)
 */
export const validateParams = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.params = await schema.parseAsync(req.params);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          acc[err.path.join('.')] = err.message;
          return acc;
        }, {} as Record<string, string>);

        return next(new ValidationError(
          'Params validation failed',
          details
        ));
      }

      next(error);
    }
  };
};
