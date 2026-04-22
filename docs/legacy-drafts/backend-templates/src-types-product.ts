// Product Tier definitions for the ML Course Platform
// Tiers: Básico → Estándar → Premium → Enterprise

export const TIER_IDS = ['basic', 'standard', 'premium', 'enterprise'] as const;
export type TierId = (typeof TIER_IDS)[number];

export interface PricingTier {
  id: TierId;
  name: { es: string; en: string };
  priceRange: { min: number; max: number };
  parameters: string[];
  deliverables: { es: string[]; en: string[] };
}

export const PRICING_TIERS: Record<TierId, PricingTier> = {
  basic: {
    id: 'basic',
    name: { es: 'Básico', en: 'Basic' },
    priceRange: { min: 0, max: 30 },
    parameters: ['p_transparencia', 'p_keywords'],
    deliverables: {
      es: ['Ebook traducido auto-draft', 'content.json básico'],
      en: ['Auto-draft translated ebook', 'Basic content.json']
    }
  },
  standard: {
    id: 'standard',
    name: { es: 'Estándar', en: 'Standard' },
    priceRange: { min: 30, max: 150 },
    parameters: ['p_transparencia', 'p_keywords', 'p_simulacion', 'p_incertidumbre'],
    deliverables: {
      es: ['Curso corto', '1 notebook', '1 visualización'],
      en: ['Short course', '1 notebook', '1 visualization']
    }
  },
  premium: {
    id: 'premium',
    name: { es: 'Premium', en: 'Premium' },
    priceRange: { min: 150, max: 800 },
    parameters: [
      'p_transparencia', 'p_keywords', 'p_simulacion',
      'p_incertidumbre', 'p_incorporacion_conocimiento', 'p_robustez'
    ],
    deliverables: {
      es: ['Curso completo', '3 notebooks', '3 visualizaciones', '5h mentoría'],
      en: ['Full course', '3 notebooks', '3 visualizations', '5h mentoring']
    }
  },
  enterprise: {
    id: 'enterprise',
    name: { es: 'Enterprise', en: 'Enterprise' },
    priceRange: { min: 800, max: Infinity },
    parameters: [
      'p_transparencia', 'p_keywords', 'p_simulacion',
      'p_incertidumbre', 'p_incorporacion_conocimiento', 'p_robustez',
      'p_validacion_regulatoria', 'p_integracion_institucional'
    ],
    deliverables: {
      es: ['Mentoría extendida', 'Repositorio privado', 'Documentación regulatoria'],
      en: ['Extended mentoring', 'Private repository', 'Regulatory documentation']
    }
  }
};

// Parameter metadata — describes each ML parameter activated per tier
export interface ParameterDef {
  id: string;
  name: { es: string; en: string };
  description: { es: string; en: string };
  minTier: TierId;
  features: string[];
}

export const PARAMETERS: ParameterDef[] = [
  {
    id: 'p_transparencia',
    name: { es: 'Transparencia', en: 'Transparency' },
    description: {
      es: 'Resúmenes explicativos del modelo y sus decisiones',
      en: 'Explanatory summaries of model decisions'
    },
    minTier: 'basic',
    features: ['model_explainers', 'introspection_notebooks']
  },
  {
    id: 'p_keywords',
    name: { es: 'Palabras clave', en: 'Keywords' },
    description: {
      es: 'Extracción automática de conceptos clave',
      en: 'Automatic extraction of key concepts'
    },
    minTier: 'basic',
    features: ['keyword_extraction', 'tag_generation']
  },
  {
    id: 'p_simulacion',
    name: { es: 'Simulación', en: 'Simulation' },
    description: {
      es: 'Generador de escenarios y demos contrafactuales',
      en: 'Scenario generator and counterfactual demos'
    },
    minTier: 'standard',
    features: ['scenario_generator', 'counterfactual_demo']
  },
  {
    id: 'p_incertidumbre',
    name: { es: 'Incertidumbre', en: 'Uncertainty' },
    description: {
      es: 'Cuantificación de incertidumbre en predicciones',
      en: 'Uncertainty quantification in predictions'
    },
    minTier: 'standard',
    features: ['confidence_intervals', 'calibration_plots']
  },
  {
    id: 'p_incorporacion_conocimiento',
    name: { es: 'Incorporación de conocimiento', en: 'Knowledge Integration' },
    description: {
      es: 'Integración de conocimiento experto en el modelo',
      en: 'Expert knowledge integration into the model'
    },
    minTier: 'premium',
    features: ['prior_injection', 'domain_constraints']
  },
  {
    id: 'p_robustez',
    name: { es: 'Robustez', en: 'Robustness' },
    description: {
      es: 'Pruebas de adversarialidad y robustez del modelo',
      en: 'Adversarial testing and model robustness'
    },
    minTier: 'premium',
    features: ['adversarial_tests', 'distribution_shift_detection']
  },
  {
    id: 'p_validacion_regulatoria',
    name: { es: 'Validación regulatoria', en: 'Regulatory Validation' },
    description: {
      es: 'Cumplimiento normativo y auditoría de modelos',
      en: 'Regulatory compliance and model auditing'
    },
    minTier: 'enterprise',
    features: ['compliance_reports', 'audit_trails']
  },
  {
    id: 'p_integracion_institucional',
    name: { es: 'Integración institucional', en: 'Institutional Integration' },
    description: {
      es: 'Despliegue e integración en infraestructura del cliente',
      en: 'Deployment and integration into client infrastructure'
    },
    minTier: 'enterprise',
    features: ['private_deployment', 'sso_integration', 'custom_api']
  }
];
