@description('The name of the project')
param projectName string = 'igshop'

@description('The environment (dev, staging, prod)')
param environment string = 'dev'

@description('The location for all resources')
param location string = 'centralus'

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

// Function App Consumption Plan
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

// Function App for API Backend
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

// Key Vault Secrets
resource openAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'openai-api-key'
  parent: keyVault
  properties: {
    value: openAiApiKey
  }
}

resource storageConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'storage-connection-string'
  parent: keyVault
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
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
output functionAppName string = functionApp.name
output applicationInsightsName string = applicationInsights.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'

output phase1Status object = {
  status: 'Core infrastructure deployed successfully'
  functionApp: 'Ready for code deployment'
  nextSteps: [
    'Deploy backend code to Function App'
    'Add PostgreSQL database (Phase 2)'
    'Configure Instagram webhooks'
  ]
} 