import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { ParsedQs } from 'qs';
import logger from '../lib/logger.js';
import { ValidationError } from '../types/errors.js';

type SchemaMap = {
  body?: ZodSchema;
  query?: ZodSchema;
  params?: ZodSchema;
};

/**
 * Generic validation interceptor that can validate body, query and params.
 * Usage: router.post('/path', validateSchemas({ body: schema }), handler)
 */
export const validateSchemas = (schemas: SchemaMap) => {
  return async (req: Request, _res: Response, next: NextFunction) => {
    try {
      // Validate body
      if (schemas.body) {
        req.body = await schemas.body.parseAsync(req.body);
      }

      // Validate query
      if (schemas.query) {
        const validatedQuery = await schemas.query.parseAsync(req.query);
        req.query = validatedQuery as unknown as ParsedQs;
      }

      // Validate params
      if (schemas.params) {
        req.params = await schemas.params.parseAsync(req.params);
      }

      return next();
    } catch (error) {
      if (error instanceof ZodError) {
        const details = error.errors.reduce((acc, err) => {
          const path = err.path.join('.') || (err.path[0] ?? '');
          acc[path] = err.message;
          return acc;
        }, {} as Record<string, string>);

        logger.warn('Validation error', {
          details,
          path: req.path,
          method: req.method,
        });

        return next(new ValidationError('Validation failed', details));
      }

      return next(error);
    }
  };
};

// Backwards-compatible exports for simple use-cases
export const validate = (schema: ZodSchema) => validateSchemas({ body: schema });
export const validateQuery = (schema: ZodSchema) => validateSchemas({ query: schema });
export const validateParams = (schema: ZodSchema) => validateSchemas({ params: schema });
