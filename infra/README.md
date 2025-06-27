# IG-Shop-Agent Infrastructure

This directory contains the Azure infrastructure deployment templates for the IG-Shop-Agent SaaS platform.

## Architecture Overview

The infrastructure includes:

- **Static Web Apps**: React frontend hosting with built-in authentication
- **App Service**: FastAPI backend API with Linux containers
- **Azure Functions**: Webhook handling and background processing
- **PostgreSQL Flexible Server**: Multi-tenant database with Row-Level Security
- **Azure AI Search**: Vector search for knowledge base
- **Azure OpenAI**: GPT-4o and embeddings for AI agent
- **Service Bus**: Message queuing for Instagram webhooks
- **Blob Storage**: File storage for catalogs, media, and licenses
- **Key Vault**: Secure secret management
- **Application Insights**: Monitoring and telemetry

## Prerequisites

1. Azure CLI installed and configured
2. An Azure subscription with appropriate permissions
3. OpenAI API access (if not using Azure OpenAI)

## Deployment

### Quick Deployment

1. Update the parameters in `parameters.dev.json`:
   ```json
   {
     "postgresAdminPassword": { "value": "YourSecurePassword123!" },
     "openAiApiKey": { "value": "your-openai-api-key" }
   }
   ```

2. Run the deployment script:
   ```bash
   # Make script executable
   chmod +x deploy.sh
   
   # Deploy to development environment
   ./deploy.sh dev igshop-dev-rg your-subscription-id
   ```

### Manual Deployment

1. Create a resource group:
   ```bash
   az group create --name igshop-dev-rg --location eastus
   ```

2. Deploy the Bicep template:
   ```bash
   az deployment group create \
     --resource-group igshop-dev-rg \
     --template-file main.bicep \
     --parameters @parameters.dev.json
   ```

## Configuration

### Environment Variables

After deployment, configure these environment variables in your applications:

#### Backend App Service
- `DATABASE_URL`: PostgreSQL connection string (from Key Vault)
- `AZURE_OPENAI_ENDPOINT`: OpenAI service endpoint
- `AZURE_OPENAI_API_KEY`: OpenAI API key
- `AZURE_SEARCH_ENDPOINT`: AI Search endpoint
- `AZURE_SEARCH_API_KEY`: AI Search admin key
- `AZURE_STORAGE_CONNECTION_STRING`: Storage account connection
- `SERVICE_BUS_CONNECTION_STRING`: Service Bus connection
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: App Insights connection

#### Function App
- Same as backend, plus:
- `WEBSITE_RUN_FROM_PACKAGE`: Set to 1 for deployment packages

### Database Initialization

Run the database migration scripts after deployment:

```bash
# Connect to PostgreSQL and run schema creation
psql "postgresql://igshop_admin:password@server.postgres.database.azure.com:5432/database" -f ../backend/migrations/001_initial_schema.sql
```

## Security Features

1. **Managed Identity**: All services use managed identity for authentication
2. **Key Vault Integration**: Secrets stored securely in Azure Key Vault
3. **Network Security**: Storage accounts block public access
4. **TLS Enforcement**: HTTPS-only configuration on all web services
5. **RBAC**: Least-privilege access assignments

## Monitoring

- **Application Insights**: Automatic telemetry collection
- **PostgreSQL Metrics**: Built-in monitoring for database performance
- **Service Bus Metrics**: Queue depth and message processing metrics
- **AI Search Analytics**: Search usage and performance tracking

## Cost Optimization

Current configuration uses basic/burstable SKUs for development:

- **PostgreSQL**: B1ms (burstable, ~$25/month)
- **App Service Plan**: B1 Linux (~$13/month)
- **AI Search**: Basic (~$250/month)
- **Storage**: Standard LRS Hot (~$5/month for 100GB)
- **Static Web Apps**: Standard (~$9/month)

Total estimated cost: ~$300/month for development environment.

## Scaling for Production

For production environments, consider:

1. **PostgreSQL**: Upgrade to General Purpose D2s_v3
2. **App Service**: Scale to P1V3 or higher
3. **AI Search**: Scale to Standard S1 with replicas
4. **OpenAI**: Monitor token usage and adjust capacity
5. **Service Bus**: Upgrade to Standard for topics/subscriptions

## Troubleshooting

### Common Issues

1. **OpenAI Region Availability**: 
   - OpenAI services are only available in specific regions
   - Update the location in main.bicep if needed

2. **Static Web Apps Region**: 
   - Limited region availability
   - Currently set to eastus2

3. **PostgreSQL Firewall**:
   - Allows Azure services by default
   - Add your IP address for direct access during development

4. **Key Vault Access**:
   - Managed identities need time to propagate
   - Wait 5-10 minutes after deployment before testing

### Getting Help

- Check Azure Activity Log for deployment errors
- Review Application Insights for runtime issues
- Use Azure Support for service-specific problems
