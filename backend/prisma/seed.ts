import { PrismaClient, Plan, Role } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // ─── Users ─────────────────────────────────────────────
  const adminPassword = await bcrypt.hash('Admin2024!@', 12);
  const studentPassword = await bcrypt.hash('Student2024!@', 12);

  const admin = await prisma.user.upsert({
    where: { email: 'admin@pmlfinance.com' },
    update: {},
    create: {
      email: 'admin@pmlfinance.com',
      password: adminPassword,
      name: 'Admin PML',
      plan: Plan.PREMIUM,
      role: Role.ADMIN,
      emailVerified: true,
    },
  });

  const instructor = await prisma.user.upsert({
    where: { email: 'instructor@pmlfinance.com' },
    update: {},
    create: {
      email: 'instructor@pmlfinance.com',
      password: adminPassword,
      name: 'Instructor PML',
      plan: Plan.PREMIUM,
      role: Role.INSTRUCTOR,
      emailVerified: true,
    },
  });

  const student = await prisma.user.upsert({
    where: { email: 'student@pmlfinance.com' },
    update: {},
    create: {
      email: 'student@pmlfinance.com',
      password: studentPassword,
      name: 'Estudiante Demo',
      plan: Plan.BASICO,
      role: Role.STUDENT,
      emailVerified: true,
    },
  });

  const santiago = await prisma.user.upsert({
    where: { email: 'xiima7716@gmail.com' },
    update: { plan: Plan.PREMIUM, role: Role.ADMIN },
    create: {
      email: 'xiima7716@gmail.com',
      password: await bcrypt.hash('pml2024', 12),
      name: 'Santiago',
      plan: Plan.PREMIUM,
      role: Role.ADMIN,
      emailVerified: true,
    },
  });

  console.log(`Users: ${admin.email}, ${instructor.email}, ${student.email}, ${santiago.email}`);

  // ─── Course ────────────────────────────────────────────
  const course = await prisma.course.upsert({
    where: { id: 'pml-finance-main' },
    update: {},
    create: {
      id: 'pml-finance-main',
      titleEs: 'ML Probabilistico para Finanzas e Inversion',
      titleEn: 'Probabilistic ML for Finance and Investing',
      descriptionEs: 'Curso completo basado en Kanungo (O\'Reilly 2023). 24 modulos, 7 capitulos, visualizaciones interactivas.',
      descriptionEn: 'Complete course based on Kanungo (O\'Reilly 2023). 24 modules, 7 chapters, interactive visualizations.',
      price: 149,
      currency: 'USD',
      status: 'PUBLISHED',
      createdById: instructor.id,
    },
  });

  // ─── Chapters ──────────────────────────────────────────
  const chaptersData = [
    { order: 1, titleEs: 'Incertidumbre', titleEn: 'Uncertainty', duration: 240 },
    { order: 2, titleEs: 'Monte Carlo', titleEn: 'Monte Carlo', duration: 180 },
    { order: 3, titleEs: 'NHST', titleEn: 'NHST', duration: 155 },
    { order: 4, titleEs: 'Framework PML', titleEn: 'PML Framework', duration: 95 },
    { order: 5, titleEs: 'IA Convencional vs PML', titleEn: 'Conventional AI vs PML', duration: 145 },
    { order: 6, titleEs: 'PyMC Ensambles', titleEn: 'PyMC Ensembles', duration: 170 },
    { order: 7, titleEs: 'Decisiones', titleEn: 'Decisions', duration: 205 },
  ];

  for (const ch of chaptersData) {
    await prisma.chapter.upsert({
      where: {
        id: `ch-${ch.order}`,
      },
      update: {},
      create: {
        id: `ch-${ch.order}`,
        courseId: course.id,
        titleEs: `Capitulo ${ch.order + 1}: ${ch.titleEs}`,
        titleEn: `Chapter ${ch.order + 1}: ${ch.titleEn}`,
        order: ch.order,
        duration: ch.duration,
      },
    });
  }

  // ─── Enrollments ───────────────────────────────────────
  await prisma.enrollment.upsert({
    where: {
      userId_courseId: { userId: student.id, courseId: course.id },
    },
    update: {},
    create: {
      userId: student.id,
      courseId: course.id,
      status: 'ACTIVE',
      progressPercent: 35,
    },
  });

  await prisma.enrollment.upsert({
    where: {
      userId_courseId: { userId: santiago.id, courseId: course.id },
    },
    update: {},
    create: {
      userId: santiago.id,
      courseId: course.id,
      status: 'ACTIVE',
      progressPercent: 100,
    },
  });

  console.log('Seed completed.');
}

main()
  .catch((e) => {
    console.error('Seed error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
