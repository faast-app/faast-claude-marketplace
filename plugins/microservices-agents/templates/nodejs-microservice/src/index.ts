import Fastify from 'fastify';
import cors from '@fastify/cors';
import { healthRoutes } from './controllers/health';
import { config } from './config/env';
import { logger } from './config/logger';

const app = Fastify({ logger });

async function start() {
  await app.register(cors, { origin: config.corsOrigins });

  // Routes
  app.register(healthRoutes);
  // app.register(exampleRoutes, { prefix: '/api/v1/examples' });

  await app.listen({ port: config.port, host: '0.0.0.0' });
}

start().catch((err) => {
  app.log.error(err);
  process.exit(1);
});
