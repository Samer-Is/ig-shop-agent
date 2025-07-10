# IG-Shop-Agent Infrastructure

This directory contains Infrastructure as Code (IaC) templates for deploying the IG-Shop-Agent multi-tenant Instagram AI agent platform.

## Architecture

The infrastructure includes:

- **PostgreSQL Flexible Server** - Multi-tenant database with row-level security
- **Azure App Service** - Flask API backend (Python 3.12)
- **Static Web Apps** - React frontend dashboard
- **Key Vault** - Secure secrets management
- **Application Insights** - Monitoring and logging
- **AI Search** - Vector search for knowledge base
- **Service Bus** - Message queue for Instagram webhooks
- **Azure Functions** - Background processing and webhooks
- **Storage Account** - File storage for media and documents

## Deployment

### Prerequisites

1. Azure CLI installed and logged in
2. Appropriate Azure subscription permissions
3. Key Vault with required secrets configured

### Deploy to Development

```bash
az deployment group create \
  --resource-group igshop-dev-rg-v2 \
  --template-file main.bicep \
  --parameters @parameters.dev.json
```

### Deploy to Staging

```bash
az deployment group create \
  --resource-group igshop-staging-rg \
  --template-file main.bicep \
  --parameters @parameters.staging.json
```

### Deploy to Production

```bash
az deployment group create \
  --resource-group igshop-prod-rg \
  --template-file main.bicep \
  --parameters @parameters.prod.json
```

## Parameters

### Required Parameters

- `environment` - Environment name (dev, staging, prod)
- `location` - Azure region for resources
- `appName` - Application name prefix
- `dbAdminLogin` - PostgreSQL administrator username
- `dbAdminPassword` - PostgreSQL administrator password (from Key Vault)

### Key Vault Secrets

The following secrets must be configured in Key Vault before deployment:

- `postgres-admin-password` - PostgreSQL administrator password
- `meta-app-id` - Facebook/Meta App ID for Instagram integration
- `meta-app-secret` - Facebook/Meta App Secret
- `openai-api-key` - OpenAI API key for AI chat functionality

## Resource Naming Convention

Resources are named using the pattern: `{appName}-{environment}-{resourceType}`

Examples:
- `igshop-dev-postgres` - Development PostgreSQL server
- `igshop-prod-api` - Production API web app
- `igshop-staging-kv` - Staging Key Vault

## Monitoring

Application Insights is automatically configured for:
- API performance monitoring
- Error tracking and alerting
- Usage analytics
- Custom telemetry from the application

## Security

- All resources use HTTPS only
- Managed Identity for secure service-to-service authentication
- Key Vault integration for secrets management
- PostgreSQL with SSL enforcement
- RBAC-based access control

## Cost Optimization

- Basic tier services for development
- Standard tier for production
- Auto-scaling enabled where supported
- 7-day backup retention to minimize storage costs

## Troubleshooting

### Common Issues

1. **Deployment fails with Key Vault access**: Ensure the deployment principal has Key Vault Secrets User role
2. **PostgreSQL connection issues**: Check firewall rules and ensure SSL is enabled
3. **Static Web App deployment**: Verify GitHub repository URL and branch name

### Logs and Monitoring

- Application logs: Available in Application Insights
- Deployment logs: Check Azure portal deployment history
- Resource logs: Enable diagnostic settings as needed 