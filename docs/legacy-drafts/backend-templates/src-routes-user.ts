import { Router } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';
import { authMiddleware, requireRole, AuthRequest } from '../middleware/auth.middleware';

const router = Router();

const UpdateUserSchema = z.object({
  name: z.string().min(1).max(100)
});

// GET /api/users/me - Get current user
router.get('/me', authMiddleware, async (req: AuthRequest, res) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.id },
      include: {
        userRoles: {
          include: {
            role: {
              include: {
                permissions: true
              }
            }
          }
        }
      }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Build response
    const roles = user.userRoles.map(ur => ur.role.name);
    const permissions = new Set<string>();
    user.userRoles.forEach(ur => {
      ur.role.permissions.forEach(p => {
        permissions.add(p.name);
      });
    });

    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        roles,
        permissions: Array.from(permissions)
      }
    });
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

// GET /api/users/:id - Get user by ID (admin only)
router.get(
  '/:id',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;

      const user = await prisma.user.findUnique({
        where: { id },
        include: {
          userRoles: {
            include: {
              role: true
            }
          }
        }
      });

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({
        success: true,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          emailVerified: user.emailVerified,
          createdAt: user.createdAt,
          roles: user.userRoles.map(ur => ur.role.name)
        }
      });
    } catch (error) {
      console.error('Error fetching user:', error);
      res.status(500).json({ error: 'Failed to fetch user' });
    }
  }
);

// PUT /api/users/me - Update current user
router.put('/me', authMiddleware, async (req: AuthRequest, res) => {
  try {
    const result = UpdateUserSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation failed',
        details: result.error.errors
      });
    }

    const updated = await prisma.user.update({
      where: { id: req.user!.id },
      data: { name: result.data.name }
    });

    // Log audit event
    await prisma.auditLog.create({
      data: {
        userId: req.user!.id,
        action: 'update:profile',
        resourceType: 'user',
        resourceId: req.user!.id,
        status: 'success',
        ipAddress: req.ip
      }
    });

    res.json({
      success: true,
      user: {
        id: updated.id,
        email: updated.email,
        name: updated.name
      }
    });
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({ error: 'Failed to update user' });
  }
});

// POST /api/users/:id/roles - Assign role to user (admin only)
router.post(
  '/:id/roles',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;
      const { roleId } = req.body;

      // Verify user and role exist
      const user = await prisma.user.findUnique({ where: { id } });
      const role = await prisma.role.findUnique({ where: { id: roleId } });

      if (!user || !role) {
        return res.status(404).json({ error: 'User or role not found' });
      }

      // Assign role
      const userRole = await prisma.userRole.create({
        data: {
          userId: id,
          roleId
        }
      });

      // Log audit event
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'assign:role',
          resourceType: 'user',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip,
          details: { roleId }
        }
      });

      res.status(201).json({
        success: true,
        userRole
      });
    } catch (error: any) {
      // Handle duplicate role assignment
      if (error.code === 'P2002') {
        return res.status(409).json({
          error: 'User already has this role'
        });
      }

      console.error('Error assigning role:', error);
      res.status(500).json({ error: 'Failed to assign role' });
    }
  }
);

// DELETE /api/users/:id/roles/:roleId - Revoke role (admin only)
router.delete(
  '/:id/roles/:roleId',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id, roleId } = req.params;

      await prisma.userRole.deleteMany({
        where: {
          userId: id,
          roleId
        }
      });

      // Log audit event
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'revoke:role',
          resourceType: 'user',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip,
          details: { roleId }
        }
      });

      res.json({ success: true, message: 'Role removed' });
    } catch (error) {
      console.error('Error revoking role:', error);
      res.status(500).json({ error: 'Failed to revoke role' });
    }
  }
);

// GET /api/users - List users (admin only)
router.get(
  '/',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const skip = Math.max(0, parseInt(req.query.skip as string) || 0);
      const take = Math.min(Math.max(1, parseInt(req.query.take as string) || 20), 100);

      const users = await prisma.user.findMany({
        skip,
        take,
        select: {
          id: true,
          email: true,
          name: true,
          emailVerified: true,
          createdAt: true,
          lastLogin: true,
          userRoles: {
            select: {
              role: {
                select: { name: true }
              }
            }
          }
        },
        orderBy: { createdAt: 'desc' }
      });

      const total = await prisma.user.count();

      res.json({
        success: true,
        users,
        pagination: {
          total,
          skip,
          take
        }
      });
    } catch (error) {
      console.error('Error fetching users:', error);
      res.status(500).json({ error: 'Failed to fetch users' });
    }
  }
);

export default router;
