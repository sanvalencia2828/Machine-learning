import { Router } from 'express';
import { createHash } from 'crypto';
import { prisma } from '../lib/prisma';
import { AuthRequest } from '../middleware/auth.middleware';

const router = Router();

// Allowed file types
const ALLOWED_TYPES = {
  'application/pdf': 'pdf',
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/webp': 'webp',
  'text/plain': 'txt',
  'text/x-python': 'py',
  'application/json': 'json'
};

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

// Generate presigned URL (stubbed - use AWS SDK in production)
async function generatePresignedUrl(s3Key: string, expiresIn: number = 3600): Promise<string> {
  // In production, use AWS SDK: s3.getSignedUrl('getObject', {...})
  return `https://bucket.s3.amazonaws.com/${s3Key}?signed=true&expires=${Date.now() + expiresIn * 1000}`;
}

// Calculate file hash
function calculateHash(buffer: Buffer): string {
  return createHash('sha256').update(buffer).digest('hex');
}

// POST /api/uploads - Upload file
router.post('/', async (req: AuthRequest, res) => {
  try {
    // In production, use multer middleware
    const { fileData, fileName, fileType } = req.body;

    // Validate file type
    if (!ALLOWED_TYPES[fileType as keyof typeof ALLOWED_TYPES]) {
      return res.status(400).json({ error: 'File type not allowed' });
    }

    // Calculate actual file size from base64 data
    const buffer = Buffer.from(fileData, 'base64');
    const fileSize = buffer.length;

    if (fileSize > MAX_FILE_SIZE) {
      return res.status(413).json({
        error: 'File too large',
        maxSize: MAX_FILE_SIZE
      });
    }
    const checksum = calculateHash(buffer);

    // Check for duplicate
    const existing = await prisma.uploadedFile.findUnique({
      where: { checksum }
    });

    if (existing && !existing.deletedAt) {
      return res.status(409).json({
        error: 'File already uploaded',
        fileId: existing.id
      });
    }

    // Generate S3 key
    const ext = ALLOWED_TYPES[fileType as keyof typeof ALLOWED_TYPES];
    const s3Key = `uploads/${req.user!.id}/${Date.now()}-${fileName}.${ext}`;

    // Save to database
    const file = await prisma.uploadedFile.create({
      data: {
        userId: req.user!.id,
        originalName: fileName,
        s3Key,
        fileType,
        fileSizeBytes: fileSize,
        checksum,
        scanStatus: 'pending' // Would be scanned asynchronously
      }
    });

    // Generate presigned URL
    const externalUrl = await generatePresignedUrl(s3Key);

    const fileWithUrl = await prisma.uploadedFile.update({
      where: { id: file.id },
      data: {
        externalUrl,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
      }
    });

    // Log audit event
    await prisma.auditLog.create({
      data: {
        userId: req.user!.id,
        action: 'upload:file',
        resourceType: 'file',
        resourceId: file.id,
        status: 'success',
        ipAddress: req.ip,
        details: { fileType, fileSize }
      }
    });

    res.status(201).json({
      success: true,
      file: {
        id: fileWithUrl.id,
        name: fileWithUrl.originalName,
        size: fileWithUrl.fileSizeBytes,
        url: fileWithUrl.externalUrl,
        expiresAt: fileWithUrl.expiresAt
      }
    });
  } catch (error) {
    console.error('Upload error:', error);

    // Log failed attempt — wrapped in try/catch to avoid masking the original error
    try {
      await prisma.auditLog.create({
        data: {
          userId: req.user!.id,
          action: 'upload:file',
          resourceType: 'file',
          status: 'failure',
          ipAddress: req.ip,
          details: { error: (error as Error).message }
        }
      });
    } catch (auditError) {
      console.error('Failed to log audit event:', auditError);
    }

    res.status(500).json({ error: 'Upload failed' });
  }
});

// GET /api/uploads/:id - Get file info
router.get('/:id', async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;

    const file = await prisma.uploadedFile.findUnique({
      where: { id }
    });

    if (!file) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Check authorization - only owner or admin
    if (file.userId !== req.user!.id && !req.user!.roles.includes('admin')) {
      return res.status(403).json({ error: 'Not authorized' });
    }

    // Refresh presigned URL if expired
    let url = file.externalUrl;
    if (file.expiresAt && file.expiresAt < new Date()) {
      url = await generatePresignedUrl(file.s3Key);
      await prisma.uploadedFile.update({
        where: { id },
        data: {
          externalUrl: url,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
        }
      });
    }

    res.json({
      success: true,
      file: {
        id: file.id,
        name: file.originalName,
        size: file.fileSizeBytes,
        type: file.fileType,
        scanStatus: file.scanStatus,
        url,
        expiresAt: file.expiresAt
      }
    });
  } catch (error) {
    console.error('Error fetching file:', error);
    res.status(500).json({ error: 'Failed to fetch file' });
  }
});

// DELETE /api/uploads/:id - Delete file
router.delete('/:id', async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;

    const file = await prisma.uploadedFile.findUnique({
      where: { id }
    });

    if (!file) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Check authorization
    if (file.userId !== req.user!.id && !req.user!.roles.includes('admin')) {
      return res.status(403).json({ error: 'Not authorized' });
    }

    // Soft delete
    await prisma.uploadedFile.update({
      where: { id },
      data: { deletedAt: new Date() }
    });

    // Log audit event
    await prisma.auditLog.create({
      data: {
        userId: req.user!.id,
        action: 'delete:file',
        resourceType: 'file',
        resourceId: id,
        status: 'success',
        ipAddress: req.ip
      }
    });

    res.json({ success: true, message: 'File deleted' });
  } catch (error) {
    console.error('Error deleting file:', error);
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

export default router;
