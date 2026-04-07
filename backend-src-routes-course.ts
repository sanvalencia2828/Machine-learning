import { Router } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';
import { authMiddleware, requireRole, AuthRequest } from '../middleware/auth.middleware';

const router = Router();

// Zod schema for course creation/update
const CourseSchema = z.object({
  titleEs: z.string().min(1),
  titleEn: z.string().min(1),
  descriptionEs: z.string().optional(),
  descriptionEn: z.string().optional(),
  price: z.number().min(0).optional(),
  collaborationStatus: z.enum(['open', 'closed', 'archived']).optional()
});

// GET /api/courses - List all published courses
router.get('/', async (req, res) => {
  try {
    const skip = Math.max(0, parseInt(req.query.skip as string) || 0);
    const take = Math.min(Math.max(1, parseInt(req.query.take as string) || 10), 100);
    const lang = (req.query.lang as string) || 'en';

    const courses = await prisma.course.findMany({
      where: { isPublished: true },
      skip,
      take,
      include: {
        chapters: {
          include: {
            figures: true,
            codeSnippets: true
          }
        },
        createdBy: {
          select: { id: true, name: true, email: true }
        }
      }
    });

    res.json({
      success: true,
      count: courses.length,
      courses
    });
  } catch (error) {
    console.error('Error fetching courses:', error);
    res.status(500).json({ error: 'Failed to fetch courses' });
  }
});

// GET /api/courses/:id - Get course details
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const course = await prisma.course.findUnique({
      where: { id },
      include: {
        chapters: {
          orderBy: { orderIndex: 'asc' },
          include: {
            figures: true,
            codeSnippets: true
          }
        },
        createdBy: {
          select: { id: true, name: true }
        }
      }
    });

    if (!course || !course.isPublished) {
      return res.status(404).json({ error: 'Course not found' });
    }

    res.json({ success: true, course });
  } catch (error) {
    console.error('Error fetching course:', error);
    res.status(500).json({ error: 'Failed to fetch course' });
  }
});

// POST /api/courses - Create new course (instructor only)
router.post(
  '/',
  authMiddleware,
  requireRole('instructor', 'admin'),
  async (req: AuthRequest, res) => {
    try {
      const data = CourseSchema.parse(req.body);

      const course = await prisma.course.create({
        data: {
          ...data,
          createdById: req.user!.id
        },
        include: {
          createdBy: { select: { id: true, name: true } }
        }
      });

      // Log audit event
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'create:course',
          resourceType: 'course',
          resourceId: course.id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.status(201).json({
        success: true,
        course
      });
    } catch (error) {
      console.error('Error creating course:', error);
      
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        });
      }

      res.status(500).json({ error: 'Failed to create course' });
    }
  }
);

// PUT /api/courses/:id - Update course
router.put(
  '/:id',
  authMiddleware,
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;
      const data = CourseSchema.partial().parse(req.body);

      // Check authorization
      const course = await prisma.course.findUnique({ where: { id } });
      
      if (!course) {
        return res.status(404).json({ error: 'Course not found' });
      }

      if (course.createdById !== req.user!.id && !req.user!.roles.includes('admin')) {
        return res.status(403).json({ error: 'Not authorized to update this course' });
      }

      const updated = await prisma.course.update({
        where: { id },
        data
      });

      // Log audit event
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'update:course',
          resourceType: 'course',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.json({ success: true, course: updated });
    } catch (error) {
      console.error('Error updating course:', error);
      res.status(500).json({ error: 'Failed to update course' });
    }
  }
);

// DELETE /api/courses/:id - Delete course (admin only)
router.delete(
  '/:id',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;

      const course = await prisma.course.findUnique({ where: { id } });
      
      if (!course) {
        return res.status(404).json({ error: 'Course not found' });
      }

      await prisma.course.delete({ where: { id } });

      // Log audit event
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'delete:course',
          resourceType: 'course',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.json({ success: true, message: 'Course deleted' });
    } catch (error) {
      console.error('Error deleting course:', error);
      res.status(500).json({ error: 'Failed to delete course' });
    }
  }
);

export default router;
