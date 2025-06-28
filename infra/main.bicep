@description('The name of the project')
param projectName string = 'igshop'

@description('The environment (dev, staging, prod)')
param environment string = 'dev'

@description('The location for all resources')
param location string = 'westus2'

@description('Administrator login for PostgreSQL')
@secure()
param postgresAdminUsername string

@description('Administrator password for PostgreSQL')
@secure()
param postgresAdminPassword string

@description('OpenAI API Key')
@secure()
param openAiApiKey string

@description('Meta/Facebook App ID')
param metaAppId string

@description('Meta/Facebook App Secret')
@secure()
param metaAppSecret string

// Variables
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 6)
var baseName = '${projectName}-${environment}-${uniqueSuffix}'

// Storage Account for blobs and static files
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${replace(baseName, '-', '')}stor'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    defaultToOAuthAuthentication: false
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

// Blob containers
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource licenseContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: 'licensefiles'
  parent: blobService
  properties: {
    publicAccess: 'None'
  }
}

resource catalogContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: 'catalog-media'
  parent: blobService
  properties: {
    publicAccess: 'None'
  }
}

resource kbContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: 'knowledge-base'
  parent: blobService
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${baseName}-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    accessPolicies: []
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${baseName}-ai'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
    RetentionInDays: 90
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// PostgreSQL Database - Azure Database for PostgreSQL Flexible Server (Minimal Tier)
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: '${baseName}-postgres'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminUsername
    administratorLoginPassword: postgresAdminPassword
    version: '15'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  name: '${baseName}_db'
  parent: postgresServer
  properties: {
    charset: 'UTF8'
    collation: 'en_US.UTF8'
  }
}

// PostgreSQL Firewall Rule to allow all Azure services
resource postgresFirewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  name: 'allow-azure-services'
  parent: postgresServer
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Note: File share removed - using Azure Database for PostgreSQL instead

// File Service for storage account
resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  name: 'default'
  parent: storageAccount
}

// Service Bus Namespace
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${baseName}-bus'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

// Service Bus Queue for Instagram messages
resource igMessageQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  name: 'ig-messages'
  parent: serviceBusNamespace
  properties: {
    defaultMessageTimeToLive: 'P1D'
    maxDeliveryCount: 3
    enableBatchedOperations: true
    deadLetteringOnMessageExpiration: true
  }
}

// Service Bus Queue for order processing
resource orderQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  name: 'order-processing'
  parent: serviceBusNamespace
  properties: {
    defaultMessageTimeToLive: 'P1D'
    maxDeliveryCount: 3
    enableBatchedOperations: true
    deadLetteringOnMessageExpiration: true
  }
}

// Note: Azure AI Search removed for cost optimization
// Using PostgreSQL pgvector extension instead

// Note: Azure OpenAI removed due to quota limitations
// Using external OpenAI API key instead (more reliable and flexible)

// Function App Consumption Plan (Ultra Low Cost - Pay per execution)
resource functionAppPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${baseName}-func-plan'
  location: location
  kind: 'functionapp'
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
  }
}

// Function App for API Backend (Ultra Low Cost)
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${baseName}-api'
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: functionAppPlan.id
    reserved: true
    isXenon: false
    hyperV: false
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: '${baseName}-api-content'
        }
        {
          name: 'DATABASE_URL'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=postgres-connection-string)'
        }
        {
          name: 'OPENAI_API_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=openai-api-key)'
        }
        {
          name: 'OPENAI_API_BASE'
          value: 'https://api.openai.com/v1'
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=storage-connection-string)'
        }
        {
          name: 'SERVICE_BUS_CONNECTION_STRING'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=servicebus-connection-string)'
        }
        {
          name: 'META_APP_ID'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=meta-app-id)'
        }
        {
          name: 'META_APP_SECRET'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=meta-app-secret)'
        }
        {
          name: 'META_WEBHOOK_VERIFY_TOKEN'
          value: '@Microsoft.KeyVault(VaultName=${keyVault.name};SecretName=meta-webhook-verify-token)'
        }
      ]
    }
    httpsOnly: true
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
  dependsOn: [keyVault, storageAccount]
}

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: '${baseName}-swa'
  location: 'eastus2' // Static Web Apps have limited region availability
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    repositoryUrl: 'https://github.com/yourusername/igshop-agent'
    branch: 'main'
    buildProperties: {
      appLocation: '/ig-shop-agent-dashboard'
      apiLocation: ''
      outputLocation: 'dist'
    }
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    provider: 'GitHub'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

// DNS Zone for custom domain (Optional - for production use)
resource dnsZone 'Microsoft.Network/dnsZones@2023-07-01-preview' = {
  name: '${baseName}.com'
  location: 'global'
  properties: {
    zoneType: 'Public'
  }
}

// Key Vault Secrets
resource postgresConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'postgres-connection-string'
  parent: keyVault
  properties: {
    value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${baseName}_db?sslmode=require'
  }
}

resource serviceBusConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'servicebus-connection-string'
  parent: keyVault
  properties: {
    value: listKeys('${serviceBusNamespace.id}/AuthorizationRules/RootManageSharedAccessKey', serviceBusNamespace.apiVersion).primaryConnectionString
  }
}

resource openAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'openai-api-key'
  parent: keyVault
  properties: {
    value: openAiApiKey
  }
}

// Note: Search service secrets removed - using pgvector instead

resource storageConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'storage-connection-string'
  parent: keyVault
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
  }
}

resource appInsightsConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'appinsights-connection-string'
  parent: keyVault
  properties: {
    value: applicationInsights.properties.ConnectionString
  }
}

resource metaAppIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'meta-app-id'
  parent: keyVault
  properties: {
    value: metaAppId
  }
}

resource metaAppSecretSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'meta-app-secret'
  parent: keyVault
  properties: {
    value: metaAppSecret
  }
}

resource metaWebhookTokenSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'meta-webhook-verify-token'
  parent: keyVault
  properties: {
    value: 'igshop-webhook-${uniqueString(resourceGroup().id)}'
  }
}

// RBAC Assignments
resource functionKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource functionStorageAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output resourceGroupName string = resourceGroup().name
output storageAccountName string = storageAccount.name
output keyVaultName string = keyVault.name
output postgresServerFQDN string = postgresServer.properties.fullyQualifiedDomainName
output serviceBusNamespace string = serviceBusNamespace.name
output openAiApiConfigured string = 'External OpenAI API configured'
output functionAppName string = functionApp.name
output staticWebAppName string = staticWebApp.name
output applicationInsightsName string = applicationInsights.name
output dnsZoneName string = dnsZone.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output postgresConnectionString string = 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${baseName}_db?sslmode=require'

// Cost Summary (Optimized Architecture)
output estimatedMonthlyCost object = {
  postgresFlexibleServer: '$35-45 (Standard_B1ms - 1 vCore, 2GB RAM, 32GB storage)'
  functionApp: '$2-5 (Consumption plan - first 1M executions free)'
  storage: '$1-3 (Free tier + minimal usage)'
  staticWebApp: '$9 (Standard tier)'
  keyVault: '$0-1 (Free tier for operations)'
  serviceBus: '$0-1 (Basic tier minimal usage)'
  externalOpenAI: '$Variable (External OpenAI API usage-based)'
  applicationInsights: '$0 (Free tier)'
  dnsZone: '$0.50 per zone per month'
  total: '$48-65/month excluding OpenAI usage'
  savings: 'Saves $200+ per month compared to original architecture'
  note: 'Using PostgreSQL Flexible Server for better reliability and pgvector support'
}
