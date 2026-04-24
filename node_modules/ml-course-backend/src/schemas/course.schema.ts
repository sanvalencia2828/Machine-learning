import { z } from 'zod';

// ============ COURSE SCHEMAS ============
export const createCourseSchema = z.object({
  titleEs: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters'),
  titleEn: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(200, 'Title must be less than 200 characters'),
  descriptionEs: z.string().max(2000).optional().nullable(),
  descriptionEn: z.string().max(2000).optional().nullable(),
  price: z.number().min(0).max(10000),
  currency: z.enum(['USD', 'EUR', 'ARS', 'MXN']).default('USD'),
  collaborationStatus: z.enum(['OPEN', 'CLOSED', 'ARCHIVED']).default('OPEN')
});

export const updateCourseSchema = createCourseSchema.partial();

export const getCourseSchema = z.object({
  id: z.string().min(1, 'Course ID is required')
});

export const listCoursesSchema = z.object({
  page: z.string().optional().default('1').transform(val => Math.max(1, parseInt(val) || 1)),
  limit: z.string().optional().default('20').transform(val => Math.max(1, Math.min(100, parseInt(val) || 20))),
  status: z.enum(['DRAFT', 'PUBLISHED', 'ARCHIVED']).optional(),
  search: z.string().optional(),
  sortBy: z.enum(['createdAt', 'title', 'price']).optional(),
  sortOrder: z.enum(['asc', 'desc']).optional().default('desc')
});

// ============ CHAPTER SCHEMAS ============
export const createChapterSchema = z.object({
  courseId: z.string().min(1, 'Course ID is required'),
  titleEs: z.string().min(2, 'Title must be at least 2 characters').max(200),
  titleEn: z.string().min(2, 'Title must be at least 2 characters').max(200),
  descriptionEs: z.string().optional().nullable(),
  descriptionEn: z.string().optional().nullable(),
  order: z.number().min(1),
  duration: z.number().optional().nullable()
});

export const updateChapterSchema = createChapterSchema.partial().omit({ courseId: true });

// ============ CONTENT SCHEMAS ============
export const createContentSchema = z.object({
  chapterId: z.string().min(1, 'Chapter ID is required'),
  type: z.enum(['TEXT', 'VIDEO', 'PDF', 'CODE', 'EXERCISE']),
  titleEs: z.string().optional().nullable(),
  titleEn: z.string().optional().nullable(),
  bodyEs: z.string().optional().nullable(),
  bodyEn: z.string().optional().nullable(),
  mediaUrl: z.string().url('Invalid media URL').optional().nullable(),
  duration: z.number().optional().nullable(),
  difficulty: z.enum(['BEGINNER', 'INTERMEDIATE', 'ADVANCED']).optional().nullable(),
  order: z.number().min(1).default(1)
});

export const updateContentSchema = createContentSchema.partial().omit({ chapterId: true });

// ============ ENROLLMENT SCHEMAS ============
export const createEnrollmentSchema = z.object({
  courseId: z.string().min(1, 'Course ID is required')
});

export const updateEnrollmentSchema = z.object({
  status: z.enum(['ACTIVE', 'PAUSED', 'COMPLETED', 'DROPPED']).optional(),
  progressPercent: z.number().min(0).max(100).optional()
});

// ============ REVIEW SCHEMAS ============
export const createReviewSchema = z.object({
  courseId: z.string().min(1, 'Course ID is required'),
  rating: z.number().min(1).max(5),
  title: z.string().min(3).max(200),
  comment: z.string().min(10).max(5000)
});

export const updateReviewSchema = createReviewSchema.partial().omit({ courseId: true });

// ============ TYPE EXPORTS ============
export type CreateCourseInput = z.infer<typeof createCourseSchema>;
export type UpdateCourseInput = z.infer<typeof updateCourseSchema>;
export type ListCoursesQuery = z.infer<typeof listCoursesSchema>;
export type CreateChapterInput = z.infer<typeof createChapterSchema>;
export type UpdateChapterInput = z.infer<typeof updateChapterSchema>;
export type CreateContentInput = z.infer<typeof createContentSchema>;
export type UpdateContentInput = z.infer<typeof updateContentSchema>;
export type CreateEnrollmentInput = z.infer<typeof createEnrollmentSchema>;
export type UpdateEnrollmentInput = z.infer<typeof updateEnrollmentSchema>;
export type CreateReviewInput = z.infer<typeof createReviewSchema>;
export type UpdateReviewInput = z.infer<typeof updateReviewSchema>;
