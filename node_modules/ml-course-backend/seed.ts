import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const hashed = await bcrypt.hash('pml2024', 12);

  await prisma.user.deleteMany({ where: { email: 'xiima7716@gmail.com' } });

  const user = await prisma.user.create({
    data: {
      email: 'xiima7716@gmail.com',
      password: hashed,
      name: 'Santiago',
      plan: 'PREMIUM',
    },
  });

  console.log(`User created: ${user.email} | Plan: ${user.plan} | ID: ${user.id}`);
  await prisma.$disconnect();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
