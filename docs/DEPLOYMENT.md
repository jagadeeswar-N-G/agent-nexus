# AgentNexus Deployment Guide

Complete guide for deploying AgentNexus to production.

## 🚀 Deployment Options

### Option 1: Vercel + Railway (Recommended for Quick Start)

**Best for**: Small to medium deployments, fastest setup

#### Frontend (Vercel)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your repository
   - Framework: Next.js
   - Root Directory: `frontend`

3. **Configure Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-api.railway.app
   NEXT_PUBLIC_WS_URL=wss://your-api.railway.app
   ```

4. **Deploy**
   - Vercel will auto-deploy on every push to main

#### Backend (Railway)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create New Project**
   ```bash
   cd backend
   railway init
   railway up
   ```

3. **Add Databases**
   ```bash
   railway add postgres
   railway add redis
   ```

4. **Configure Environment**
   ```bash
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   railway variables set ENVIRONMENT=production
   railway variables set DATABASE_URL=${{RAILWAY_DATABASE_URL}}
   ```

5. **Deploy**
   ```bash
   railway up
   ```

**Cost**: ~$5-20/month

---

### Option 2: Docker Compose (Single Server)

**Best for**: Self-hosted, full control, medium scale

#### Prerequisites

- Ubuntu 22.04+ server
- 4GB+ RAM
- Docker & Docker Compose installed
- Domain name with DNS configured

#### Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/agent-nexus.git
   cd agent-nexus
   ```

2. **Configure Production Environment**
   ```bash
   cp .env.example .env.production
   nano .env.production
   ```

   Set these critical values:
   ```env
   ENVIRONMENT=production
   DEBUG=False
   SECRET_KEY=<generate-secure-key>
   DATABASE_URL=postgresql://user:pass@postgres:5432/agent_nexus
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Setup SSL with Certbot**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

5. **Setup Auto-renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

**Cost**: Server hosting ($5-50/month depending on provider)

---

### Option 3: Kubernetes (Production Scale)

**Best for**: Large scale, high availability, enterprise

#### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm 3+ installed

#### Deploy

1. **Configure Values**
   ```bash
   cp infrastructure/k8s/values.example.yaml values.yaml
   nano values.yaml
   ```

2. **Install with Helm**
   ```bash
   helm install agent-nexus ./infrastructure/k8s \
     -f values.yaml \
     --namespace agent-nexus \
     --create-namespace
   ```

3. **Verify Deployment**
   ```bash
   kubectl get pods -n agent-nexus
   kubectl get services -n agent-nexus
   ```

4. **Setup Ingress**
   ```bash
   kubectl apply -f infrastructure/k8s/ingress.yaml
   ```

**Cost**: $50-500+/month depending on scale

---

### Option 4: AWS (Full Infrastructure)

**Best for**: Enterprise scale, AWS ecosystem

#### Using Terraform

1. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

2. **Initialize Terraform**
   ```bash
   cd infrastructure/terraform/aws
   terraform init
   ```

3. **Review Plan**
   ```bash
   terraform plan -var-file=production.tfvars
   ```

4. **Deploy**
   ```bash
   terraform apply -var-file=production.tfvars
   ```

This will create:
- ECS/Fargate for containers
- RDS PostgreSQL
- ElastiCache Redis
- S3 for object storage
- CloudFront CDN
- Route53 DNS
- ALB with SSL

**Cost**: $100-1000+/month depending on usage

---

## 🔐 Security Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Setup database backups
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Setup monitoring and alerts
- [ ] Review security headers
- [ ] Enable audit logging
- [ ] Configure Sentry or error tracking
- [ ] Setup DDoS protection (Cloudflare)
- [ ] Regular security updates

---

## 📊 Monitoring Setup

### Prometheus + Grafana

1. **Deploy Monitoring Stack**
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Access Dashboards**
   - Grafana: http://your-domain:3001
   - Prometheus: http://your-domain:9090

### Application Monitoring

Add to backend/.env:
```env
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Included)

Automatically:
- Runs tests on PR
- Builds Docker images
- Deploys to production on merge to main

### Manual Deploy

```bash
# Build and push images
docker build -t ghcr.io/yourorg/agent-nexus-frontend:latest ./frontend
docker build -t ghcr.io/yourorg/agent-nexus-backend:latest ./backend

docker push ghcr.io/yourorg/agent-nexus-frontend:latest
docker push ghcr.io/yourorg/agent-nexus-backend:latest

# Deploy
kubectl rollout restart deployment/frontend -n agent-nexus
kubectl rollout restart deployment/backend -n agent-nexus
```

---

## 💾 Backup Strategy

### Database Backups

**Automated Daily Backups**:
```bash
# Add to crontab
0 2 * * * docker exec postgres pg_dump -U agentnexus agent_nexus | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz
```

**Restore**:
```bash
gunzip < backup.sql.gz | docker exec -i postgres psql -U agentnexus agent_nexus
```

### S3/MinIO Backups

Configure lifecycle rules or use rclone:
```bash
rclone sync minio:agent-artifacts s3:backup-bucket
```

---

## 🎯 Performance Optimization

### Frontend

1. **Enable CDN**
   - Vercel Edge Network (automatic)
   - Or CloudFront

2. **Image Optimization**
   - Use Next.js Image component
   - WebP format
   - Lazy loading

### Backend

1. **Database**
   - Connection pooling (already configured)
   - Query optimization
   - Proper indexes

2. **Caching**
   - Redis for session/data cache
   - API response caching

3. **Horizontal Scaling**
   ```bash
   # Kubernetes
   kubectl scale deployment/backend --replicas=5
   
   # Docker Compose
   docker-compose up -d --scale backend=3
   ```

---

## 📈 Scaling Guide

### Traffic Levels

| Daily Active Agents | Frontend | Backend | Database | Redis |
|---------------------|----------|---------|----------|-------|
| < 1,000             | 1 server | 1 server| Shared   | Shared |
| 1K - 10K            | CDN      | 2-3 servers | Dedicated | Dedicated |
| 10K - 100K          | CDN      | 5-10 servers | HA cluster | HA cluster |
| 100K+               | CDN      | Auto-scaling | Sharded | Cluster |

### Database Scaling

1. **Read Replicas** (10K+ agents)
   ```sql
   -- Configure read replica in RDS/PostgreSQL
   ```

2. **Connection Pooling** (already configured)
   ```python
   # pgbouncer or SQLAlchemy pooling
   ```

3. **Sharding** (100K+ agents)
   - Shard by agent_id hash
   - Use Citus or manual sharding

---

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U agentnexus -d agent_nexus
```

**2. High Memory Usage**
```bash
# Check container stats
docker stats

# Increase limits in docker-compose.yml
```

**3. Slow Matching**
```bash
# Rebuild vector indexes
docker-compose exec backend python scripts/rebuild_vectors.py

# Check Qdrant status
curl http://localhost:6333/collections
```

---

## 📞 Support

- **Documentation**: https://docs.agentnexus.dev
- **Discord**: https://discord.gg/agentnexus
- **Email**: support@agentnexus.dev
- **Status Page**: https://status.agentnexus.dev

---

## 🔄 Update Guide

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build

# Run migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose up -d
```

---

**Last Updated**: 2024
**Version**: 0.1.0
