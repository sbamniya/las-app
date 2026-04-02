"""FuzeBox AEOS Constants — Framework Definitions"""

# CAITO Pillar Definitions
CAITO_PILLARS = {
    "culture": {
        "name": "Culture",
        "code": "C",
        "description": "Organizational readiness, leadership commitment, change capacity",
        "dimensions": [
            "leadership_commitment",
            "change_capacity",
            "innovation_culture",
            "risk_tolerance",
            "ai_vision_clarity",
            "cross_functional_collaboration",
            "data_driven_decision_making",
        ],
    },
    "architecture": {
        "name": "Architecture",
        "code": "A",
        "description": "AEOS 12-layer infrastructure, cloud maturity, security posture, data platform",
        "dimensions": [
            "cloud_maturity",
            "api_availability",
            "data_infrastructure",
            "security_posture",
            "scalability",
            "integration_readiness",
            "compute_capacity",
        ],
    },
    "integration": {
        "name": "Integration",
        "code": "I",
        "description": "System connectivity, MCP connectors, API availability, data quality",
        "dimensions": [
            "system_connectivity",
            "data_quality",
            "workflow_automation",
            "mcp_readiness",
            "api_coverage",
            "real_time_data_flow",
            "interoperability",
        ],
    },
    "talent": {
        "name": "Talent",
        "code": "T",
        "description": "Workforce skill distribution, AI literacy, learning velocity, agent planning",
        "dimensions": [
            "skill_distribution",
            "learning_velocity",
            "ai_literacy",
            "adaptability",
            "technical_depth",
            "change_readiness",
            "agent_collaboration_skills",
        ],
    },
}

CAITO_OUTCOMES = {
    "name": "Outcomes",
    "code": "O",
    "description": "Measurable KPIs, AI-ROI, tracking, business impact quantification",
    "dimensions": [
        "kpi_definition",
        "measurement_capability",
        "business_impact_tracking",
        "roi_methodology",
        "continuous_improvement",
    ],
}

# Dynamic weight presets based on transformation goals
TRANSFORMATION_WEIGHT_PRESETS = {
    "cost_reduction": {"culture": 0.15, "architecture": 0.25, "integration": 0.35, "talent": 0.25},
    "revenue_growth": {"culture": 0.30, "architecture": 0.20, "integration": 0.25, "talent": 0.25},
    "automation": {"culture": 0.15, "architecture": 0.30, "integration": 0.35, "talent": 0.20},
    "workforce_augmentation": {"culture": 0.35, "architecture": 0.15, "integration": 0.15, "talent": 0.35},
    "agent_deployment": {"culture": 0.15, "architecture": 0.30, "integration": 0.35, "talent": 0.20},
    "digital_transformation": {"culture": 0.25, "architecture": 0.25, "integration": 0.25, "talent": 0.25},
    "compliance_governance": {"culture": 0.20, "architecture": 0.30, "integration": 0.30, "talent": 0.20},
}

# GSTI weight presets
GSTI_WEIGHT_PRESETS = {
    "agent_deployment": {"culture": 0.15, "architecture": 0.30, "integration": 0.35, "talent": 0.20},
    "workforce_augmentation": {"culture": 0.35, "architecture": 0.15, "integration": 0.15, "talent": 0.35},
    "balanced": {"culture": 0.25, "architecture": 0.25, "integration": 0.25, "talent": 0.25},
}

# Agent Score thresholds
AGENT_SCORE_THRESHOLDS = {
    "execute": 0.55,
    "manual_review_min": 0.40,
    "manual_review_max": 0.55,
    "suppress": 0.40,
}

# Agent grading scale
AGENT_GRADE_SCALE = {
    "A": 0.90,
    "B": 0.80,
    "C": 0.70,
    "D": 0.60,
    "F": 0.0,
}

# Assessment modes
ASSESSMENT_MODES = {
    "quick_scan": {
        "name": "Quick Scan",
        "duration": "5 minutes",
        "depth": "surface",
        "questions_per_pillar": 2,
        "follow_up_depth": 1,
    },
    "executive": {
        "name": "Executive Assessment",
        "duration": "15-20 minutes",
        "depth": "moderate",
        "questions_per_pillar": 4,
        "follow_up_depth": 2,
    },
    "deep_diagnostic": {
        "name": "Deep Diagnostic",
        "duration": "45-60 minutes",
        "depth": "comprehensive",
        "questions_per_pillar": 7,
        "follow_up_depth": 3,
    },
}

# Industry vertical definitions
INDUSTRY_VERTICALS = {
    "gaming_hospitality": {
        "name": "Gaming & Hospitality",
        "key_workflows": [
            "player_loyalty_optimization",
            "revenue_management",
            "compliance_monitoring",
            "guest_experience",
            "fraud_detection",
        ],
        "regulatory_requirements": ["gaming_commission", "aml", "responsible_gaming"],
        "benchmark_multipliers": {"architecture": 1.1, "integration": 1.2, "culture": 0.9, "talent": 0.95},
    },
    "healthcare": {
        "name": "Healthcare",
        "key_workflows": [
            "prior_authorization",
            "clinical_documentation",
            "revenue_cycle",
            "patient_scheduling",
            "compliance_reporting",
        ],
        "regulatory_requirements": ["hipaa", "clinical_accuracy", "audit_trails"],
        "benchmark_multipliers": {"architecture": 1.15, "integration": 1.1, "culture": 1.05, "talent": 1.1},
    },
    "financial_services": {
        "name": "Financial Services",
        "key_workflows": [
            "risk_assessment",
            "transaction_monitoring",
            "compliance_screening",
            "fraud_detection",
            "customer_onboarding",
        ],
        "regulatory_requirements": ["soc2", "regulatory_reporting", "explainability"],
        "benchmark_multipliers": {"architecture": 1.2, "integration": 1.15, "culture": 1.0, "talent": 1.1},
    },
    "enterprise_saas": {
        "name": "Enterprise SaaS",
        "key_workflows": [
            "customer_support_automation",
            "product_analytics",
            "billing_optimization",
            "onboarding_automation",
            "churn_prediction",
        ],
        "regulatory_requirements": ["soc2", "gdpr", "data_privacy"],
        "benchmark_multipliers": {"architecture": 1.1, "integration": 1.05, "culture": 1.1, "talent": 1.15},
    },
    "automotive": {
        "name": "Automotive",
        "key_workflows": [
            "vehicle_acquisition_pricing",
            "lifecycle_management",
            "service_optimization",
            "compliance_monitoring",
            "inventory_management",
        ],
        "regulatory_requirements": ["manufacturer_compliance", "financial_controls", "regulatory_reporting"],
        "benchmark_multipliers": {"architecture": 1.0, "integration": 1.2, "culture": 0.95, "talent": 1.0},
    },
    "higher_education": {
        "name": "Higher Education",
        "key_workflows": [
            "transfer_credit_evaluation",
            "financial_aid_validation",
            "enrollment_verification",
            "academic_advising",
            "research_compliance",
        ],
        "regulatory_requirements": ["accreditation", "ferpa", "title_iv"],
        "benchmark_multipliers": {"architecture": 0.9, "integration": 1.1, "culture": 1.15, "talent": 1.1},
    },
    "manufacturing": {
        "name": "Manufacturing",
        "key_workflows": [
            "supply_chain_optimization",
            "vendor_risk_monitoring",
            "quality_assurance",
            "procurement_automation",
            "predictive_maintenance",
        ],
        "regulatory_requirements": ["quality_standards", "supplier_compliance", "osha"],
        "benchmark_multipliers": {"architecture": 1.05, "integration": 1.2, "culture": 0.9, "talent": 0.95},
    },
}
