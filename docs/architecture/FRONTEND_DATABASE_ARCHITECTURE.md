# 🎨 Arquitectura Frontend + Database: Guía Profesional

---

## PARTE 1: ARQUITECTURA FRONTEND (Next.js)

### 1.1 Estructura de Carpetas Recomendada

#### Actual (Incompleta)
```
dashboard/
├── src/
│   ├── app/              # AppRouter
│   ├── components/       # Componentes mixtos
│   └── lib/              # Utilidades
```

#### ✅ Profesional
```
dashboard/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/
│   │   │   ├── courses/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── profile/
│   │   │   └── layout.tsx
│   │   ├── api/routes/               # Route handlers
│   │   │   ├── auth/
│   │   │   ├── courses/
│   │   │   └── webhooks/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── error.tsx
│   │
│   ├── components/
│   │   ├── ui/                       # Componentes reutilizables
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Dialog.tsx
│   │   │   ├── Form/
│   │   │   ├── Layout/
│   │   │   └── Navigation/
│   │   │
│   │   ├── features/                 # Componentes de features
│   │   │   ├── AuthForms/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── CourseListing/
│   │   │   ├── UserProfile/
│   │   │   └── common/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   │
│   │   └── providers/                # Providers globales
│   │       ├── AuthProvider.tsx
│   │       ├── ThemeProvider.tsx
│   │       └── ToastProvider.tsx
│   │
│   ├── hooks/                        # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── usePagination.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── lib/
│   │   ├── api-client.ts             # HTTP client
│   │   ├── auth.ts                   # Auth logic
│   │   ├── constants.ts              # Constantes
│   │   ├── utils.ts                  # Funciones helper
│   │   └── validators.ts             # Validación de forms
│   │
│   ├── store/                        # State management (Zustand)
│   │   ├── auth.store.ts
│   │   ├── ui.store.ts
│   │   └── index.ts
│   │
│   ├── types/
│   │   ├── api.ts                    # API response types
│   │   ├── entities.ts               # Domain types
│   │   └── index.ts
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── tailwind.config.ts
│   │
│   └── middleware.ts                 # Next.js middleware
│
├── public/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── __tests__/                        # Tests
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── e2e/
│
├── .env.example
├── .env.local                        # NO COMMIT
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── jest.config.js
└── package.json
```

---

### 1.2 API Client Profesional

```typescript
// src/lib/api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth.store';

class ApiClient {
  private instance: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

    this.instance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Version': process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'
      }
    });

    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Agregar correlation ID
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();
        
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado - refresh o logout
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }

        if (error.response?.status === 403) {
          // No tiene permisos
          window.location.href = '/unauthorized';
        }

        return Promise.reject(error.response?.data || error);
      }
    );
  }

  private generateCorrelationId(prefix: string = 'req'): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Métodos genéricos
  get<T>(url: string, config?: AxiosRequestConfig) {
    return this.instance.get<never, T>(url, config);
  }

  post<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.post<never, T>(url, data, config);
  }

  put<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.put<never, T>(url, data, config);
  }

  patch<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.patch<never, T>(url, data, config);
  }

  delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.instance.delete<never, T>(url, config);
  }
}

export const apiClient = new ApiClient();
```

### 1.3 Custom Hooks Profesionales

```typescript
// src/hooks/useApi.ts
import { useState, useCallback, useRef } from 'react';
import { apiClient } from '@/lib/api-client';

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  manual?: boolean; // Si es true, no llama automáticamente
}

export function useApi<T = any>(
  url: string,
  options: UseApiOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!options.manual);
  const [error, setError] = useState<any>(null);
  const isMounted = useRef(true);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.get<T>(url);
      
      if (isMounted.current) {
        setData(result);
        options.onSuccess?.(result);
      }
      
      return result;
    } catch (err) {
      if (isMounted.current) {
        setError(err);
        options.onError?.(err);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [url, options]);

  return { data, loading, error, execute };
}

// src/hooks/useAuth.ts
import { useCallback } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { apiClient } from '@/lib/api-client';

interface LoginInput {
  email: string;
  password: string;
}

export function useAuth() {
  const { user, token, setAuth, logout: storeLogout } = useAuthStore();

  const login = useCallback(async (input: LoginInput) => {
    try {
      const response = await apiClient.post<{ token: string; user: any }>(
        '/auth/login',
        input
      );
      
      setAuth(response.token, response.user);
      return response;
    } catch (error) {
      throw error;
    }
  }, [setAuth]);

  const logout = useCallback(async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      storeLogout();
    }
  }, [storeLogout]);

  const register = useCallback(async (input: any) => {
    const response = await apiClient.post<{ token: string; user: any }>(
      '/auth/register',
      input
    );
    
    setAuth(response.token, response.user);
    return response;
  }, [setAuth]);

  return { user, token, login, logout, register, isAuthenticated: !!token };
}

// src/hooks/usePagination.ts
import { useState, useCallback } from 'react';

export interface PaginationState {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}

export function usePagination(initialLimit: number = 20) {
  const [state, setState] = useState<PaginationState>({
    page: 1,
    limit: initialLimit,
    total: 0,
    hasMore: false
  });

  const setTotal = useCallback((total: number) => {
    setState(prev => ({
      ...prev,
      total,
      hasMore: prev.page * prev.limit < total
    }));
  }, []);

  const nextPage = useCallback(() => {
    setState(prev => {
      if (prev.hasMore) {
        return { ...prev, page: prev.page + 1 };
      }
      return prev;
    });
  }, []);

  const prevPage = useCallback(() => {
    setState(prev => ({
      ...prev,
      page: Math.max(1, prev.page - 1)
    }));
  }, []);

  const goToPage = useCallback((page: number) => {
    setState(prev => ({
      ...prev,
      page: Math.max(1, page)
    }));
  }, []);

  return { ...state, setTotal, nextPage, prevPage, goToPage };
}
```

### 1.4 State Management (Zustand)

```bash
npm install zustand
```

```typescript
// src/store/auth.store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  roles: string[];
  avatar?: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,
      
      setAuth: (token: string, user: User) => {
        set({ token, user });
        localStorage.setItem('authToken', token);
      },
      
      logout: () => {
        set({ user: null, token: null });
        localStorage.removeItem('authToken');
      },
      
      setUser: (user: User) => {
        set({ user });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token, 
        user: state.user 
      })
    }
  )
);

// src/store/ui.store.ts
interface UiStore {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  
  toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  
  addNotification: (notification) => set(state => ({
    notifications: [...state.notifications, notification]
  })),
  
  removeNotification: (id) => set(state => ({
    notifications: state.notifications.filter(n => n.id !== id)
  }))
}));
```

### 1.5 Tipos TypeScript

```typescript
// src/types/api.ts
export interface ApiResponse<T = any> {
  code: string;
  message: string;
  data?: T;
  errors?: Record<string, string>;
  meta?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
  meta: {
    timestamp: string;
    correlationId: string;
  };
}

// src/types/entities.ts
export interface Course {
  id: string;
  titleEs: string;
  titleEn: string;
  descriptionEs?: string;
  descriptionEn?: string;
  price: number;
  currency: string;
  isPublished: boolean;
  createdAt: string;
  updatedAt: string;
  creator: {
    id: string;
    name: string;
    email: string;
  };
  chapters?: Chapter[];
}

export interface Chapter {
  id: string;
  titleEs: string;
  titleEn: string;
  courseId: string;
  order: number;
  contents?: Content[];
  createdAt: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  roles: string[];
  createdAt: string;
}
```

---

## PARTE 2: ARQUITECTURA DE BASE DE DATOS

### 2.1 Esquema Prisma Mejorado

```prisma
// prisma/schema.prisma

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

// ============ USERS & AUTH ============
model User {
  id                String      @id @default(cuid())
  email             String      @unique
  emailVerified     DateTime?
  name              String?
  avatar            String?
  
  // OAuth
  oauthProvider     String?     // "google", "github", "microsoft"
  oauthId           String?
  
  // Password-based auth
  passwordHash      String?
  passwordSalt      String?
  passwordChangedAt DateTime?
  
  // Status
  isActive          Boolean     @default(true)
  lastLogin         DateTime?
  lastActivity      DateTime?
  
  // Preferences
  preferredLanguage String      @default("es") // es, en
  theme             String      @default("light") // light, dark
  emailNotifications Boolean    @default(true)
  
  // Audit
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt
  deletedAt         DateTime?   @db.Timestamp(6)

  // Relations
  userRoles         UserRole[]
  courses           Course[]    @relation("createdBy")
  enrollments       Enrollment[]
  auditLogs         AuditLog[]
  sessions          Session[]
  uploadedFiles     UploadedFile[]
  settings          UserSettings?

  @@unique([oauthProvider, oauthId])
  @@index([email])
  @@index([isActive])
  @@map("users")
}

model UserSettings {
  id                String      @id @default(cuid())
  userId            String      @unique
  notificationEmail String?
  privacyLevel      String      @default("public") // public, private, friends
  metadata          Json?
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_settings")
}

model Role {
  id                String      @id @default(cuid())
  name              String      @unique // "ADMIN", "INSTRUCTOR", "STUDENT", "VIEWER"
  description       String?
  isSystem          Boolean     @default(false) // Roles del sistema no se pueden borrar
  createdAt         DateTime    @default(now())

  userRoles         UserRole[]
  rolePermissions   RolePermission[]

  @@index([name])
  @@map("roles")
}

model Permission {
  id                String      @id @default(cuid())
  name              String      @unique // "courses:create", "users:read", etc
  description       String?
  resource          String      // "courses", "users", "enrollments"
  action            String      // "read", "create", "update", "delete"
  createdAt         DateTime    @default(now())

  rolePermissions   RolePermission[]

  @@unique([resource, action])
  @@index([resource])
  @@map("permissions")
}

model UserRole {
  id                String      @id @default(cuid())
  userId            String
  roleId            String
  courseId          String?     // Rol a nivel de curso
  grantedAt         DateTime    @default(now())
  grantedBy         String?     // User who granted this role
  expiresAt         DateTime?   // Expiration date for temporary roles

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  role              Role        @relation(fields: [roleId], references: [id], onDelete: Restrict)
  course            Course?     @relation(fields: [courseId], references: [id], onDelete: Cascade)

  @@unique([userId, roleId, courseId])
  @@index([userId])
  @@index([courseId])
  @@map("user_roles")
}

model RolePermission {
  id                String      @id @default(cuid())
  roleId            String
  permissionId      String

  role              Role        @relation(fields: [roleId], references: [id], onDelete: Cascade)
  permission        Permission  @relation(fields: [permissionId], references: [id], onDelete: Cascade)

  @@unique([roleId, permissionId])
  @@map("role_permissions")
}

// ============ COURSES & CONTENT ============
model Course {
  id                String      @id @default(cuid())
  slug              String      @unique
  code              String      @unique @db.VarChar(10)
  
  titleEs           String      @db.VarChar(255)
  titleEn           String      @db.VarChar(255)
  descriptionEs     String?     @db.Text
  descriptionEn     String?     @db.Text
  
  coverImage        String?     // URL or S3 key
  price             Decimal     @default(0) @db.Decimal(10, 2)
  currency          String      @default("USD") @db.Char(3)
  
  // Status tracking
  status            String      @default("DRAFT") // DRAFT, PUBLISHED, ARCHIVED
  isPublished       Boolean     @default(false)
  publishedAt       DateTime?
  
  // Collaboration
  collaborationStatus String    @default("OPEN") // OPEN, CLOSED, ARCHIVED
  
  // Versioning
  version           Int         @default(1)
  previousVersionId String?
  
  // SEO
  seoTitle          String?
  seoDescription    String?
  seoKeywords       Json?       // Array of keywords
  
  // Metadata & Analytics
  viewCount         Int         @default(0)
  enrollmentCount   Int         @default(0)
  ratingAverage     Decimal?    @db.Decimal(3, 2)
  reviewCount       Int         @default(0)
  
  metadata          Json?
  
  // Audit
  createdById       String
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt
  deletedAt         DateTime?

  // Relations
  createdBy         User        @relation("createdBy", fields: [createdById], references: [id])
  chapters          Chapter[]
  enrollments       Enrollment[]
  userRoles         UserRole[]
  reviews           Review[]
  tags              CourseTag[]

  @@index([slug])
  @@index([status])
  @@index([isPublished])
  @@index([createdById])
  @@index([createdAt])
  @@map("courses")
}

model Chapter {
  id                String      @id @default(cuid())
  courseId          String
  order             Int
  
  titleEs           String
  titleEn           String
  descriptionEs     String?
  descriptionEn     String?
  
  duration          Int?        // en minutos
  estimatedCompletion Float?    // en horas
  
  isPublished       Boolean     @default(false)
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt
  deletedAt         DateTime?

  course            Course      @relation(fields: [courseId], references: [id], onDelete: Cascade)
  contents          Content[]
  lessons           Lesson[]    @relation("chapter_lessons")

  @@unique([courseId, order])
  @@index([courseId])
  @@index([isPublished])
  @@map("chapters")
}

model Content {
  id                String      @id @default(cuid())
  chapterId         String
  type              String      // TEXT, VIDEO, PDF, CODE, EXERCISE
  order             Int
  
  titleEs           String?
  titleEn           String?
  bodyEs            String?     @db.Text
  bodyEn            String?     @db.Text
  
  // Media
  mediaUrl          String?
  mediaType         String?     // video/mp4, application/pdf, etc
  duration          Int?        // segundos
  
  // Tags
  tags              String[]    @default([])
  difficulty        String?     // BEGINNER, INTERMEDIATE, ADVANCED
  
  isPublished       Boolean     @default(false)
  metadata          Json?
  
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt

  chapter           Chapter     @relation(fields: [chapterId], references: [id], onDelete: Cascade)

  @@index([chapterId])
  @@index([type])
  @@map("contents")
}

model Lesson {
  id                String      @id @default(cuid())
  chapterId         String
  order             Int
  
  titleEs           String
  titleEn           String
  
  objectives        Json        // Array of learning objectives
  duration          Int?
  difficulty        String?
  
  isPublished       Boolean     @default(false)
  createdAt         DateTime    @default(now())

  chapter           Chapter     @relation("chapter_lessons", fields: [chapterId], references: [id], onDelete: Cascade)
  submissions       LessonSubmission[]

  @@unique([chapterId, order])
  @@map("lessons")
}

// ============ ENROLLMENTS ============
model Enrollment {
  id                String      @id @default(cuid())
  userId            String
  courseId          String
  
  status            String      @default("ACTIVE") // ACTIVE, PAUSED, COMPLETED, DROPPED
  progressPercent   Int         @default(0)
  lastAccessAt      DateTime?
  
  completedAt       DateTime?
  certificateUrl    String?
  
  metadata          Json?       // Custom enrollment data
  
  enrolledAt        DateTime    @default(now())
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  course            Course      @relation(fields: [courseId], references: [id], onDelete: Cascade)
  progress          EnrollmentProgress[]

  @@unique([userId, courseId])
  @@index([userId])
  @@index([courseId])
  @@index([status])
  @@map("enrollments")
}

model EnrollmentProgress {
  id                String      @id @default(cuid())
  enrollmentId      String
  contentId         String
  
  status            String      @default("NOT_STARTED") // NOT_STARTED, IN_PROGRESS, COMPLETED
  startedAt         DateTime?
  completedAt       DateTime?
  duration          Int?        // tiempo gastado en segundos
  
  score             Decimal?    @db.Decimal(5, 2)
  feedback          String?
  
  updatedAt         DateTime    @updatedAt

  enrollment        Enrollment  @relation(fields: [enrollmentId], references: [id], onDelete: Cascade)

  @@unique([enrollmentId, contentId])
  @@index([enrollmentId])
  @@map("enrollment_progress")
}

// ============ REVIEWS ============
model Review {
  id                String      @id @default(cuid())
  courseId          String
  userId            String
  
  rating            Int         @default(5) // 1-5
  title             String
  comment           String      @db.Text
  
  verified          Boolean     @default(false) // Verified purchase
  helpful           Int         @default(0)
  unhelpful         Int         @default(0)
  
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt

  course            Course      @relation(fields: [courseId], references: [id], onDelete: Cascade)

  @@unique([courseId, userId])
  @@index([courseId])
  @@index([rating])
  @@map("reviews")
}

// ============ TAGS ============
model Tag {
  id                String      @id @default(cuid())
  name              String      @unique
  slug              String      @unique
  description       String?
  
  courseCount       Int         @default(0)

  courses           CourseTag[]

  @@map("tags")
}

model CourseTag {
  id                String      @id @default(cuid())
  courseId          String
  tagId             String

  course            Course      @relation(fields: [courseId], references: [id], onDelete: Cascade)
  tag               Tag         @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@unique([courseId, tagId])
  @@map("course_tags")
}

// ============ FILES ============
model UploadedFile {
  id                String      @id @default(cuid())
  userId            String
  
  fileName          String
  originalName      String
  mimeType          String
  size              Int         // bytes
  
  s3Key             String      @unique
  s3Etag            String?
  s3Url             String
  
  // Meta
  duration          Int?        // para videos, en segundos
  width             Int?        // para imágenes
  height            Int?
  
  status            String      @default("PROCESSING") // PROCESSING, READY, FAILED
  metadata          Json?
  
  uploadedAt        DateTime    @default(now())

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([s3Key])
  @@map("uploaded_files")
}

// ============ SESSIONS & AUDIT ============
model Session {
  id                String      @id @default(cuid())
  userId            String
  
  token             String      @unique
  refreshToken      String?     @unique
  
  ipAddress         String?
  userAgent         String?
  isActive          Boolean     @default(true)
  
  expiresAt         DateTime
  lastActivity      DateTime    @default(now())
  createdAt         DateTime    @default(now())

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([expiresAt])
  @@map("sessions")
}

model AuditLog {
  id                String      @id @default(cuid())
  userId            String
  action            String      // "CREATE", "UPDATE", "DELETE"
  resource          String      // "course", "user", "enrollment"
  resourceId        String
  
  changes           Json?       // Delta de cambios
  ipAddress         String?
  userAgent         String?
  
  createdAt         DateTime    @default(now())

  user              User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([resource])
  @@index([createdAt])
  @@map("audit_logs")
}

model LessonSubmission {
  id                String      @id @default(cuid())
  lessonId          String
  userId            String
  
  content           String?     @db.Text
  score             Decimal?    @db.Decimal(5, 2)
  feedback          String?
  
  submittedAt       DateTime    @default(now())

  lesson            Lesson      @relation(fields: [lessonId], references: [id], onDelete: Cascade)

  @@index([lessonId])
  @@map("lesson_submissions")
}
```

### 2.2 Índices Críticos y Optimización

```sql
-- Crear índices adicionales para performance
CREATE INDEX idx_users_email_active ON users(email, is_active);
CREATE INDEX idx_courses_status_published ON courses(status, is_published, created_at DESC);
CREATE INDEX idx_enrollments_user_status ON enrollments(user_id, status);
CREATE INDEX idx_enrollments_course_status ON enrollments(course_id, status);
CREATE INDEX idx_progress_enrollment_status ON enrollment_progress(enrollment_id, status);
CREATE INDEX idx_enrollments_created_at ON enrollments(created_at DESC);
CREATE INDEX idx_courses_created_by_published ON courses(created_by_id, is_published);

-- Para búsquedas de texto
CREATE INDEX idx_courses_title_search ON courses(title_es, title_en);

-- Índices compuestos para queries frecuentes
CREATE INDEX idx_user_course_enrollment ON enrollments(user_id, course_id);
CREATE INDEX idx_chapter_course_order ON chapters(course_id, "order");
```

### 2.3 Database Connection Pooling

```bash
npm install pg-boss # Para background jobs
```

```typescript
// src/lib/db-pool.ts
import { Pool, PoolClient } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  
  // Pool settings
  max: 20,                              // Maximum pool size
  min: 5,                               // Minimum pool size
  idleTimeoutMillis: 30000,             // 30 segundos
  connectionTimeoutMillis: 2000,
  
  // Performance
  statement_timeout: 30000,             // 30 seconds
  idle_in_transaction_session_timeout: 30000,
  
  // Support prepared statements
  connectionString: process.env.DATABASE_URL
});

pool.on('error', (err) => {
  logger.error('Unexpected error on idle client', err);
});

pool.on('connect', () => {
  logger.debug('New connection to database');
});

export const query = (text: string, params?: any[]) => {
  const id = Math.random() * 1000;
  const start = Date.now();
  
  return pool
    .query(text, params)
    .then(res => {
      const duration = Date.now() - start;
      if (duration > 1000) {
        logger.warn(`Slow query detected (${duration}ms)`, { text });
      }
      return res.rows;
    })
    .catch(err => {
      logger.error('Database error', { text, error: err.message });
      throw err;
    });
};

export const getClient = (): Promise<PoolClient> => pool.connect();
export const closePool = () => pool.end();
```

---

## Checklist de Implementación

### Base de Datos
- [ ] Ejecutar migración con nuevo schema
- [ ] Crear índices recomendados
- [ ] Configurar backups diarios
- [ ] Implementar connection pooling
- [ ] Agregar archivos de seeds

### Frontend
- [ ] Reorganizar carpetas
- [ ] Crear API client
- [ ] Implementar custom hooks
- [ ] Configurar Zustand
- [ ] Agregar tipos TypeScript
- [ ] Implementar error boundaries

### Testing
- [ ] Unit tests para utils
- [ ] Integration tests para API
- [ ] E2E tests para flujos críticos

---

## Próximos Pasos

1. **Implementar logging y error handling en backend** (2 días)
2. **Reorganizar frontend** (1-2 días)
3. **Mejorar database schema** (1 día)
4. **Agregar tests** (2-3 días)
5. **Documentación API** (1 día)

Total estimado: **1-2 semanas** para una arquitectura profesional completa.
