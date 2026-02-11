#!/bin/bash

# AgentNexus - Project Structure Setup
# This script creates the complete directory structure

echo "🚀 Creating AgentNexus project structure..."

# Root directories
mkdir -p frontend/{src,public}
mkdir -p backend/{app,tests}
mkdir -p docs
mkdir -p .github/{workflows,ISSUE_TEMPLATE}
mkdir -p infrastructure/{docker,k8s,terraform}
mkdir -p scripts

# Frontend structure
mkdir -p frontend/src/{app,components,lib,hooks,types,styles}
mkdir -p frontend/src/app/{api,auth,dashboard,agents,matches,collaborate}
mkdir -p frontend/src/components/{ui,agent,matching,collaboration,layout}
mkdir -p frontend/public/{icons,images}

# Backend structure
mkdir -p backend/app/{api,core,models,schemas,services,db,auth,utils}
mkdir -p backend/app/api/{v1,websocket}
mkdir -p backend/app/api/v1/{endpoints}
mkdir -p backend/app/services/{matching,orchestrator,reputation,collaboration}
mkdir -p backend/tests/{unit,integration,e2e}

# Infrastructure
mkdir -p infrastructure/docker/{frontend,backend,nginx}
mkdir -p infrastructure/k8s/{base,overlays}
mkdir -p infrastructure/terraform/{aws,gcp,azure}

# Documentation
mkdir -p docs/{guides,api,security,deployment}

echo "✅ Directory structure created!"
echo "📦 Total directories: $(find . -type d | wc -l)"
