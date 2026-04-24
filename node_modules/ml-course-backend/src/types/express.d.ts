import 'express';

declare global {
  namespace Express {
    interface Request {
      /** correlation id injected by middleware */
      id?: string;
      /** alias for correlation id */
      correlationId?: string;
      /** authenticated user context is declared per-app (do not define here) */
    }
  }
}

export {};
