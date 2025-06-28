const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Mock data
const products = [
  {
    id: "prod_1",
    name: "قميص أبيض",
    name_en: "White Shirt",
    price: 25.00,
    currency: "JOD",
    description: "قميص أبيض عالي الجودة",
    description_en: "High quality white shirt",
    image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
    in_stock: true,
    category: "clothing"
  },
  {
    id: "prod_2",
    name: "بنطال جينز",
    name_en: "Jeans Pants",
    price: 45.00,
    currency: "JOD",
    description: "بنطال جينز مريح",
    description_en: "Comfortable jeans pants",
    image: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
    in_stock: true,
    category: "clothing"
  },
  {
    id: "prod_3",
    name: "حذاء رياضي",
    name_en: "Sports Shoes",
    price: 65.00,
    currency: "JOD",
    description: "حذاء رياضي مريح",
    description_en: "Comfortable sports shoes",
    image: "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
    in_stock: true,
    category: "shoes"
  }
];

// Routes
app.get('/', (req, res) => {
  res.json({
    message: "IG-Shop-Agent API is running",
    status: "healthy",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    endpoints: {
      health: "/health",
      auth: "/auth/login",
      catalog: "/catalog",
      webhook: "/webhook/instagram"
    }
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    version: "1.0.0"
  });
});

app.get('/catalog', (req, res) => {
  res.json({
    products: products,
    total: products.length,
    page: 1,
    per_page: 10
  });
});

app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  if (email && password) {
    res.json({
      success: true,
      token: "mock_jwt_token_123",
      user: {
        id: "user_123",
        email: email,
        name: "Test User",
        business_name: "محل الموضة",
        business_name_en: "Fashion Store"
      }
    });
  } else {
    res.status(400).json({
      error: "Email and password required"
    });
  }
});

// Instagram webhook verification
app.get('/webhook/instagram', (req, res) => {
  const { 'hub.mode': hubMode, 'hub.challenge': hubChallenge, 'hub.verify_token': hubVerifyToken } = req.query;
  
  const verifyToken = process.env.META_WEBHOOK_VERIFY_TOKEN || 'ig_shop_webhook_verify_123';
  
  console.log('Webhook verification:', { hubMode, hubVerifyToken, verifyToken });
  
  if (hubMode === 'subscribe' && hubVerifyToken === verifyToken) {
    console.log('Instagram webhook verified successfully');
    res.send(hubChallenge);
  } else {
    console.log('Instagram webhook verification failed');
    res.status(403).send('Forbidden');
  }
});

// Instagram webhook handler
app.post('/webhook/instagram', (req, res) => {
  const body = req.body;
  console.log('Instagram webhook received:', body);
  
  // Process webhook data here
  if (body.object === 'instagram') {
    res.send('OK');
  } else {
    res.status(400).send('Invalid payload');
  }
});

// 404 handler for Azure health checks (Azure pings random URLs)
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.originalUrl,
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ IG-Shop-Agent API running on port ${PORT}`);
  console.log(`🌍 API Base URL: http://localhost:${PORT}`);
  console.log(`📊 Health Check: http://localhost:${PORT}/health`);
  console.log(`🛍️ Catalog: http://localhost:${PORT}/catalog`);
  console.log(`🔐 Auth: http://localhost:${PORT}/auth/login`);
  console.log(`📱 Instagram Webhook: http://localhost:${PORT}/webhook/instagram`);
}); 