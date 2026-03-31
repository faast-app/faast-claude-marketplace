import { FastifyInstance } from 'fastify';

export async function healthRoutes(app: FastifyInstance) {
  app.get('/health', async () => ({
    status: 'healthy',
    service: '{{ServiceName}}',
    timestamp: new Date().toISOString(),
  }));
}
