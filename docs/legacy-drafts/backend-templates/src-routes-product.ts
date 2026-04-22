import { Router } from 'express';
import { z } from 'zod';
import { prisma } from '../lib/prisma';
import { authMiddleware, requireRole, AuthRequest } from '../middleware/auth.middleware';
import {
  PRICING_TIERS, PARAMETERS, TIER_IDS,
  type TierId
} from '../types/product';

const router = Router();

// --- Validation schemas ---

const CreateProductSchema = z.object({
  type: z.enum(['ebook', 'course', 'mentoring']),
  tierId: z.enum(TIER_IDS),
  titleEs: z.string().min(1).max(200),
  titleEn: z.string().min(1).max(200),
  descriptionEs: z.string().max(2000).optional(),
  descriptionEn: z.string().max(2000).optional(),
  price: z.number().min(0),
  summaryEs: z.string().max(1000).optional(),
  summaryEn: z.string().max(1000).optional(),
  sourceRef: z.string().optional(),
  parameters: z.array(z.string()).optional()
});

const UpdateProductSchema = CreateProductSchema.partial();

// --- Helper: validate price fits the tier ---

function validatePriceForTier(price: number, tierId: TierId): string | null {
  const tier = PRICING_TIERS[tierId];
  if (price < tier.priceRange.min) {
    return `Price $${price} is below minimum $${tier.priceRange.min} for tier "${tierId}"`;
  }
  if (tier.priceRange.max !== Infinity && price > tier.priceRange.max) {
    return `Price $${price} exceeds maximum $${tier.priceRange.max} for tier "${tierId}"`;
  }
  return null;
}

// --- Helper: validate parameters belong to tier ---

function validateParametersForTier(params: string[], tierId: TierId): string | null {
  const allowedParams = PRICING_TIERS[tierId].parameters;
  const invalid = params.filter(p => !allowedParams.includes(p));
  if (invalid.length > 0) {
    return `Parameters not available in tier "${tierId}": ${invalid.join(', ')}`;
  }
  return null;
}

// ============================================================
// PUBLIC ENDPOINTS
// ============================================================

// GET /api/products/tiers - List all pricing tiers (public)
router.get('/tiers', (_req, res) => {
  res.json({
    success: true,
    tiers: Object.values(PRICING_TIERS)
  });
});

// GET /api/products/tiers/:tierId - Get tier details with parameters
router.get('/tiers/:tierId', (req, res) => {
  const { tierId } = req.params;

  if (!TIER_IDS.includes(tierId as TierId)) {
    return res.status(404).json({ error: 'Tier not found' });
  }

  const tier = PRICING_TIERS[tierId as TierId];
  const tierParams = PARAMETERS.filter(p => tier.parameters.includes(p.id));

  res.json({
    success: true,
    tier,
    parameters: tierParams
  });
});

// GET /api/products/parameters - List all ML parameters
router.get('/parameters', (_req, res) => {
  res.json({
    success: true,
    parameters: PARAMETERS
  });
});

// GET /api/products - List published products (public storefront)
router.get('/', async (req, res) => {
  try {
    const skip = Math.max(0, parseInt(req.query.skip as string) || 0);
    const take = Math.min(Math.max(1, parseInt(req.query.take as string) || 12), 50);
    const type = req.query.type as string | undefined;
    const tierId = req.query.tier as string | undefined;
    const lang = (req.query.lang as string) || 'en';

    const where: Record<string, unknown> = { isPublished: true };
    if (type) where.type = type;
    if (tierId) where.tierId = tierId;

    const [products, total] = await Promise.all([
      prisma.product.findMany({
        where,
        skip,
        take,
        orderBy: { createdAt: 'desc' },
        include: {
          createdBy: { select: { id: true, name: true } }
        }
      }),
      prisma.product.count({ where })
    ]);

    // Map to localized response
    const localized = products.map(p => ({
      id: p.id,
      type: p.type,
      tierId: p.tierId,
      title: lang === 'es' ? p.titleEs : p.titleEn,
      description: lang === 'es' ? p.descriptionEs : p.descriptionEn,
      summary: lang === 'es' ? p.summaryEs : p.summaryEn,
      price: p.price,
      parameters: p.parameters,
      tier: PRICING_TIERS[p.tierId as TierId],
      createdBy: p.createdBy,
      createdAt: p.createdAt
    }));

    res.json({
      success: true,
      products: localized,
      pagination: { total, skip, take }
    });
  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

// GET /api/products/:id - Get product detail
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const lang = (req.query.lang as string) || 'en';

    const product = await prisma.product.findUnique({
      where: { id },
      include: {
        createdBy: { select: { id: true, name: true } }
      }
    });

    if (!product || !product.isPublished) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const tier = PRICING_TIERS[product.tierId as TierId];
    const tierParams = PARAMETERS.filter(p => tier?.parameters.includes(p.id));

    res.json({
      success: true,
      product: {
        id: product.id,
        type: product.type,
        tierId: product.tierId,
        title: lang === 'es' ? product.titleEs : product.titleEn,
        description: lang === 'es' ? product.descriptionEs : product.descriptionEn,
        summary: lang === 'es' ? product.summaryEs : product.summaryEn,
        price: product.price,
        parameters: product.parameters,
        createdBy: product.createdBy,
        createdAt: product.createdAt
      },
      tier,
      availableParameters: tierParams
    });
  } catch (error) {
    console.error('Error fetching product:', error);
    res.status(500).json({ error: 'Failed to fetch product' });
  }
});

// ============================================================
// ADMIN / INSTRUCTOR ENDPOINTS
// ============================================================

// POST /api/products - Create a product (instructor/admin)
router.post(
  '/',
  authMiddleware,
  requireRole('instructor', 'admin'),
  async (req: AuthRequest, res) => {
    try {
      const data = CreateProductSchema.parse(req.body);

      // Validate price is within tier range
      const priceError = validatePriceForTier(data.price, data.tierId);
      if (priceError) {
        return res.status(400).json({ error: priceError });
      }

      // Validate parameters belong to selected tier
      if (data.parameters) {
        const paramError = validateParametersForTier(data.parameters, data.tierId);
        if (paramError) {
          return res.status(400).json({ error: paramError });
        }
      }

      // Default parameters to tier's full set if not provided
      const parameters = data.parameters ?? PRICING_TIERS[data.tierId].parameters;

      const product = await prisma.product.create({
        data: {
          type: data.type,
          tierId: data.tierId,
          titleEs: data.titleEs,
          titleEn: data.titleEn,
          descriptionEs: data.descriptionEs,
          descriptionEn: data.descriptionEn,
          summaryEs: data.summaryEs,
          summaryEn: data.summaryEn,
          price: data.price,
          sourceRef: data.sourceRef,
          parameters,
          createdById: req.user!.id
        },
        include: {
          createdBy: { select: { id: true, name: true } }
        }
      });

      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'create:product',
          resourceType: 'product',
          resourceId: product.id,
          status: 'success',
          ipAddress: req.ip,
          details: { type: data.type, tierId: data.tierId, price: data.price }
        }
      });

      res.status(201).json({ success: true, product });
    } catch (error) {
      console.error('Error creating product:', error);

      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: 'Validation failed', details: error.errors });
      }

      res.status(500).json({ error: 'Failed to create product' });
    }
  }
);

// PUT /api/products/:id - Update product
router.put(
  '/:id',
  authMiddleware,
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;
      const data = UpdateProductSchema.parse(req.body);

      const product = await prisma.product.findUnique({ where: { id } });

      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }

      if (product.createdById !== req.user!.id && !req.user!.roles.includes('admin')) {
        return res.status(403).json({ error: 'Not authorized' });
      }

      // Use existing tier if not changing it
      const effectiveTier = (data.tierId ?? product.tierId) as TierId;

      if (data.price !== undefined) {
        const priceError = validatePriceForTier(data.price, effectiveTier);
        if (priceError) {
          return res.status(400).json({ error: priceError });
        }
      }

      if (data.parameters) {
        const paramError = validateParametersForTier(data.parameters, effectiveTier);
        if (paramError) {
          return res.status(400).json({ error: paramError });
        }
      }

      const updated = await prisma.product.update({
        where: { id },
        data
      });

      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'update:product',
          resourceType: 'product',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.json({ success: true, product: updated });
    } catch (error) {
      console.error('Error updating product:', error);
      res.status(500).json({ error: 'Failed to update product' });
    }
  }
);

// PATCH /api/products/:id/publish - Toggle publish status
router.patch(
  '/:id/publish',
  authMiddleware,
  requireRole('instructor', 'admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;

      const product = await prisma.product.findUnique({ where: { id } });

      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }

      if (product.createdById !== req.user!.id && !req.user!.roles.includes('admin')) {
        return res.status(403).json({ error: 'Not authorized' });
      }

      const updated = await prisma.product.update({
        where: { id },
        data: { isPublished: !product.isPublished }
      });

      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: updated.isPublished ? 'publish:product' : 'unpublish:product',
          resourceType: 'product',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.json({
        success: true,
        product: updated,
        message: updated.isPublished ? 'Product published' : 'Product unpublished'
      });
    } catch (error) {
      console.error('Error toggling publish:', error);
      res.status(500).json({ error: 'Failed to update publish status' });
    }
  }
);

// DELETE /api/products/:id - Delete product (admin only)
router.delete(
  '/:id',
  authMiddleware,
  requireRole('admin'),
  async (req: AuthRequest, res) => {
    try {
      const { id } = req.params;

      const product = await prisma.product.findUnique({ where: { id } });
      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }

      await prisma.product.delete({ where: { id } });

      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'delete:product',
          resourceType: 'product',
          resourceId: id,
          status: 'success',
          ipAddress: req.ip
        }
      });

      res.json({ success: true, message: 'Product deleted' });
    } catch (error) {
      console.error('Error deleting product:', error);
      res.status(500).json({ error: 'Failed to delete product' });
    }
  }
);

export default router;
