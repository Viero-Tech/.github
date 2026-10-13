import { defineConfig } from 'prisma/config';

// validate and format only check the URL shape, so a placeholder lets them
// run without a database. migrate commands read the real DATABASE_URL.
const databaseUrl =
  process.env.DATABASE_URL ?? 'postgresql://placeholder:placeholder@localhost:5432/placeholder';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
  },
  datasource: {
    url: databaseUrl,
  },
});
