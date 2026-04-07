export enum ResponseCode {
  SUCCESS = 'SUCCESS',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  BAD_REQUEST = 'BAD_REQUEST'
}

export interface ApiError {
  code: ResponseCode;
  message: string;
  statusCode: number;
  details?: Record<string, any>;
  timestamp: string;
  correlationId?: string;
}

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: ResponseCode;
  public readonly details?: Record<string, any>;

  constructor(
    code: ResponseCode,
    message: string,
    statusCode: number,
    details?: Record<string, any>
  ) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;

    Error.captureStackTrace(this, this.constructor);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(ResponseCode.VALIDATION_ERROR, message, 400, details);
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required') {
    super(ResponseCode.AUTHENTICATION_ERROR, message, 401);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Insufficient permissions') {
    super(ResponseCode.AUTHORIZATION_ERROR, message, 403);
    Object.setPrototypeOf(this, AuthorizationError.prototype);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id?: string) {
    const message = id 
      ? `${resource} with id '${id}' not found`
      : `${resource} not found`;
    super(ResponseCode.NOT_FOUND, message, 404);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

export class ConflictError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(ResponseCode.CONFLICT, message, 409, details);
    Object.setPrototypeOf(this, ConflictError.prototype);
  }
}

export class BadRequestError extends AppError {
  constructor(message: string, details?: Record<string, any>) {
    super(ResponseCode.BAD_REQUEST, message, 400, details);
    Object.setPrototypeOf(this, BadRequestError.prototype);
  }
}

export class DatabaseError extends AppError {
  constructor(message: string = 'Database operation failed', details?: Record<string, any>) {
    super(ResponseCode.DATABASE_ERROR, message, 500, details);
    Object.setPrototypeOf(this, DatabaseError.prototype);
  }
}

export class RateLimitError extends AppError {
  constructor(message: string = 'Rate limit exceeded', details?: Record<string, any>) {
    super(ResponseCode.RATE_LIMIT_ERROR, message, 429, details);
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }
}
