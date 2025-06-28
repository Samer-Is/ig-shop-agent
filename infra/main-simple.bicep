// IG-Shop-Agent Ultra Low-Cost Infrastructure (Simplified - No Quota Issues)
@description('Project name used as prefix for resources')
param projectName string = 'igshop'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('PostgreSQL admin username')
param postgresAdminUsername string

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('OpenAI API Key (existing)')
@secure()
param openAiApiKey string

@description('Meta App ID')
param metaAppId string

@description('Meta App Secret')
@secure()
param metaAppSecret string

// Variables
var baseName = '${projectName}-${environment}'
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 6)

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${baseName}st${uniqueSuffix}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

// File Share for PostgreSQL data persistence
resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  name: '${storageAccount.name}/default/postgres-data'
  properties: {
    shareQuota: 50
  }
}

// Key Vault for secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${baseName}-kv-${uniqueSuffix}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
  }
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${baseName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${baseName}-ai'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
  }
}

// PostgreSQL Container Instance
resource postgresContainer 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: '${baseName}-postgres'
  location: location
  properties: {
    containers: [
      {
        name: 'postgres'
        properties: {
          image: 'ankane/pgvector:latest'
          resources: {
            requests: {
              cpu: 1
              memoryInGB: 2
            }
          }
          ports: [
            {
              port: 5432
              protocol: 'TCP'
            }
          ]
          environmentVariables: [
            {
              name: 'POSTGRES_DB'
              value: '${baseName}_db'
            }
            {
              name: 'POSTGRES_USER'
              value: postgresAdminUsername
            }
            {
              name: 'POSTGRES_PASSWORD'
              secureValue: postgresAdminPassword
            }
            {
              name: 'POSTGRES_INITDB_ARGS'
              value: '--auth-host=scram-sha-256'
            }
          ]
          volumeMounts: [
            {
              name: 'postgres-storage'
              mountPath: '/var/lib/postgresql/data'
            }
          ]
        }
      }
    ]
    restartPolicy: 'Always'
    osType: 'Linux'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 5432
          protocol: 'TCP'
        }
      ]
    }
    volumes: [
      {
        name: 'postgres-storage'
        azureFile: {
          shareName: 'postgres-data'
          storageAccountName: storageAccount.name
          storageAccountKey: storageAccount.listKeys().keys[0].value
        }
      }
    ]
  }
  dependsOn: [fileShare]
}

// Service Bus Namespace
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${baseName}-sb-${uniqueSuffix}'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

// Service Bus Queue
resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  name: 'messages'
  parent: serviceBusNamespace
  properties: {
    maxSizeInMegabytes: 1024
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount: 10
  }
}

// App Service Plan (Consumption)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${baseName}-asp'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: false
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${baseName}-functions'
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: '${baseName}-api-content'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
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
}

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: '${baseName}-swa'
  location: 'eastus2'
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    allowConfigFileUpdates: true
    provider: 'None'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

// Key Vault Secrets
resource postgresConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'postgres-connection-string'
  parent: keyVault
  properties: {
    value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresContainer.properties.ipAddress.fqdn}:5432/${baseName}_db'
  }
}

resource openAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'openai-api-key'
  parent: keyVault
  properties: {
    value: openAiApiKey
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
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output resourceGroupName string = resourceGroup().name
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output postgresConnectionString string = 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresContainer.properties.ipAddress.fqdn}:5432/${baseName}_db'

// Ultra Low Cost Summary
output costSummary object = {
  postgresContainer: '$15-20/month (1 CPU, 2GB RAM)'
  functionApp: '$2-5/month (Consumption plan)'
  storage: '$1-3/month (Standard LRS)'
  staticWebApp: '$9/month (Standard tier)'
  keyVault: '$0-1/month (Standard operations)'
  serviceBus: '$0-1/month (Basic tier)'
  openAI: 'Your existing API usage'
  total: '$27-39/month + OpenAI usage'
  savings: '95% cost reduction vs original $800+/month'
} 