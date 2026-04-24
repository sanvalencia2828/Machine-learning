import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const hashed = await bcrypt.hash('pml2024', 12);

  const user = await prisma.user.upsert({
    where: { email: 'xiima7716@gmail.com' },
    update: { password: hashed, name: 'Santiago', plan: 'PREMIUM' },
    create: {
      email: 'xiima7716@gmail.com',
      password: hashed,
      name: 'Santiago',
      plan: 'PREMIUM',
    },
  });

  console.log(`User: ${user.email} | Plan: ${user.plan} | ID: ${user.id}`);

  const count = await prisma.user.count();
  console.log(`Total users: ${count}`);

  await prisma.$disconnect();
}

main().catch((e) => {
  console.error('Error:', e);
  process.exit(1);
});
