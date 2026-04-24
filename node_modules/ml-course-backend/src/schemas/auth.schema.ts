import { z } from 'zod';

const passwordRules = z
  .string()
  .min(12, 'Password must be at least 12 characters')
  .refine((v) => /[A-Z]/.test(v), { message: 'Password must contain at least one uppercase letter' })
  .refine((v) => /[a-z]/.test(v), { message: 'Password must contain at least one lowercase letter' })
  .refine((v) => /[0-9]/.test(v), { message: 'Password must contain at least one number' })
  .refine((v) => /[^A-Za-z0-9]/.test(v), { message: 'Password must contain at least one special character' });

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: passwordRules,
  name: z.string().min(1, 'Name is required').max(100),
});

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

export const updatePlanSchema = z.object({
  plan: z.enum(['FREE', 'BASICO', 'AVANZADO', 'PREMIUM']),
});

export type RegisterInput = z.infer<typeof registerSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type UpdatePlanInput = z.infer<typeof updatePlanSchema>;
