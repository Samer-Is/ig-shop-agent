# IG Shop Agent Dashboard

A comprehensive frontend dashboard for the Instagram DM automation SaaS platform, built with React, TypeScript, and TailwindCSS.

## 🌟 Features

### 📊 Dashboard Overview
- Real-time metrics and KPIs
- Performance indicators (customer satisfaction, response time, conversion rate)
- Recent orders and conversations display
- Revenue vs AI cost tracking

### 📦 Product Catalog Management
- Complete product CRUD operations
- CSV import/export functionality
- Stock management and low stock alerts
- Category-based filtering
- Multi-language product descriptions (Arabic/English)

### 🛒 Order Management
- Order tracking and status updates
- Customer information management
- Order details with delivery information
- Status-based filtering and search

### 💬 Conversation Interface
- Real-time conversation monitoring
- AI vs human message differentiation
- Conversation threading by customer
- Message history with context tracking
- Manual intervention capabilities

### 📚 Knowledge Base
- Document upload and management
- Vector indexing status tracking
- Content preview and search
- File type and size management
- Processing status indicators

### 🏢 Business Profile Configuration
- Comprehensive business information setup
- Operating hours management
- Policy configuration (shipping, returns, payment)
- AI personality customization
- Multi-language tone settings

### 📈 Analytics & Reporting
- Revenue and cost analysis
- Conversation trends and statistics
- Customer satisfaction metrics
- Top product performance
- Interactive charts and visualizations

### ⚙️ Settings & Configuration
- Notification preferences
- AI agent configuration
- Instagram API integration
- Security settings (password, 2FA)
- Webhook management

## 🎨 Design Features

### Visual Excellence
- Modern, professional interface design
- Consistent color palette and typography
- Responsive layout for all screen sizes
- Intuitive navigation and user experience
- Bilingual support (Arabic/English)

### UI Components
- Custom-designed components with shadcn/ui
- Professional data tables and forms
- Interactive charts with Recharts
- Modal dialogs and dropdown menus
- Status badges and progress indicators

## 🛠 Technical Stack

- **Frontend Framework**: React 18.3 with TypeScript
- **Build Tool**: Vite 6.0
- **Styling**: TailwindCSS 3.4
- **UI Components**: shadcn/ui component library
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **Routing**: React Router v6
- **Package Manager**: pnpm

## 📱 Mock Data & Context

The dashboard includes comprehensive mock data representing a real Jordanian fashion store:

- **Business**: Jordan Fashion Store (@jordanfashion_store)
- **Products**: Traditional Arabic fashion items with local pricing in JOD
- **Conversations**: AI responses in Jordanian Arabic dialect
- **Orders**: Realistic order data with local addresses
- **Analytics**: Performance metrics and growth trends

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- pnpm package manager

### Installation & Development
```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

### Project Structure
```
src/
├── components/        # UI components
│   ├── layout/       # Layout components (Sidebar, Header)
│   └── ui/           # Reusable UI components
├── pages/            # Page components
├── types/            # TypeScript type definitions
├── data/             # Mock data and constants
├── lib/              # Utility functions
└── hooks/            # Custom React hooks
```

## 🌍 Deployment

The application is deployed and accessible at: https://1i10pz1sw2.space.minimax.io

### Build Output
- Optimized production build
- Code splitting for performance
- Gzip compression enabled
- Static asset optimization

## 🎯 Key Features Demonstrated

1. **Multi-tenant SaaS Interface**: Professional dashboard suitable for enterprise use
2. **Bilingual Support**: Seamless Arabic/English content management
3. **Real-time Monitoring**: Live conversation and order tracking
4. **AI Integration UI**: Settings and monitoring for AI agent behavior
5. **Comprehensive Analytics**: Business intelligence and performance metrics
6. **Professional Design**: Enterprise-grade visual design and UX

## 📊 Business Metrics Displayed

- Total Conversations: 1,523 (+12.5%)
- Active Orders: 28 (+8.2%)
- Monthly Revenue: 8,750 JOD (+23.1%)
- AI Cost: $342.50 (-5.3%)
- Customer Satisfaction: 4.8/5 stars
- Conversion Rate: 18.5%

## 🔐 Security Features

- Secure authentication interface
- API key management
- Webhook security configuration
- User permission management
- Data privacy controls

## 🎨 Visual Design Philosophy

The interface follows modern SaaS design principles with:
- Clean, minimalist aesthetic
- Professional color palette (blues, purples, grays)
- Consistent spacing and typography
- Accessible design patterns
- Mobile-responsive layout

## 📝 Notes

This is a frontend-only implementation with comprehensive mock data. In a production environment, this would connect to the FastAPI backend with real-time data synchronization, authentication, and API integrations.

The design specifically caters to the Middle Eastern market with appropriate cultural considerations, Arabic language support, and local business practices.
