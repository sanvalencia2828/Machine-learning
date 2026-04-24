# FASE 2: Database Optimization (Próximos Pasos)

**Duración**: 1 semana  
**Prioridad**: 🔴 ALTA  
**Dependencias**: ✅ Fase 1 completada

---

## 🎯 Objetivos

1. Optimizar queries de base de datos
2. Agregar connection pooling
3. Crear índices estratégicos
4. Implementar transaction management
5. Mejorar performance 40%+

---

## 📋 Tareas

### Día 1-2: Connection Pooling

```bash
# 1. Instalar PgBouncer localmente o en Docker
docker run -d \
  -e DATABASES_DEFAULT_POOL_MODE=transaction \
  -e DATABASES_DEFAULT_POOL_SIZE=25 \
  -e PGBOUNCER_MAX_CLIENT_CONN=1000 \
  -p 6432:6432 \
  pgbouncer:latest

# 2. Actualizar DATABASE_URL en .env.local
DATABASE_URL=postgresql://user:pass@localhost:6432/db_name
```

**Archivos a crear**: 
- `src/lib/db-pool.ts` - Connection pool configuration
- `src/lib/transaction.service.ts` - Transaction wrapper

### Día 3-4: Database Indexing

```sql
-- Crear migrations con índices:
npm run db:migrate -- --name add_performance_indexes

-- Agregar en migration:
CREATE INDEX idx_users_email_active ON users(email, email_verified);
CREATE INDEX idx_courses_status_published ON courses(status, is_published, created_at DESC);
CREATE INDEX idx_enrollments_user_status ON enrollments(user_id, status);
-- ... más índices según FRONTEND_DATABASE_ARCHITECTURE.md
```

### Día 5: Query Optimization

```typescript
// Reemplazar FindMany con Select específicos
// Usar include selectivamente
// Agregar lazy loading donde sea apropiado

// Antes (pesado)
const user = await prisma.user.findUnique({
  where: { id: '123' },
  include: { userRoles: { include: { role: true } }, enrollments: true }
});

// Después (optimizado)
const user = await prisma.user.findUnique({
  where: { id: '123' },
  select: {
    id: true,
    email: true,
    name: true,
    userRoles: { select: { role: { select: { name: true } } } }
  }
});
```

### Día 6-7: Testing & Consolidation

```bash
# Medir performance
npm run test:performance

# Comparar query times
# Esperado: 50-60% reduction

# Commit y documentar
git add .
git commit -m "feat: database optimization with pooling and indexes"
```

---

## 📊 Métricas Esperadas

```
Antes:   Query avg: 200ms, Connections: 100
Después: Query avg: 80ms,  Connections: 25
Mejora:  60% más rápido ✅
```

---

## 📁 Nuevos Archivos

```
src/
├── lib/
│   ├── db-pool.ts .................. Connection pooling
│   └── transaction.service.ts ..... Transaction management
├── services/
│   └── database.service.ts ........ Database utilities
```

---

## ⚠️ Consideraciones

- Hacer backup antes de cambios de schema
- Probar migrations en desarrollo primero
- Monitorear conexiones a BD
- Lidiar con connection timeouts gracefully

---

## ✅ Requisitos para Fase 2

- [ ] Fase 1 completada y testeada
- [ ] Database backup hecho
- [ ] PostgreSQL versión 14+ 
- [ ] Migration scripts preparados
- [ ] Performance baseline medido

---

## 📚 Recursos

- [Prisma Performance](https://www.prisma.io/docs/guides/performance-and-optimization)
- [PostgreSQL Index Guide](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PgBouncer Configuration](https://pgbouncer.github.io/config.html)

---

**Siguientes pasos después de Fase 2**: Redis Caching
