import rTracer from 'cls-rtracer';

// cls-rtracer genera un ID unico por request y lo mantiene
// accesible en todo el call stack via AsyncLocalStorage.
// Usar rTracer.id() en cualquier parte del codigo para obtenerlo.
export const correlationIdMiddleware = rTracer.expressMiddleware({
  useHeader: true,
  headerName: 'X-Correlation-ID',
  echoHeader: true,
});
