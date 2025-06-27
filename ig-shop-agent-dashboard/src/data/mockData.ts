import { 
  Tenant, 
  User, 
  CatalogItem, 
  Order, 
  Conversation, 
  BusinessProfile, 
  KBDocument, 
  UsageStats,
  DashboardStats 
} from '../types';

// Current tenant data
export const currentTenant: Tenant = {
  id: 'tenant-123',
  instagram_handle: '@jordanfashion_store',
  display_name: 'Jordan Fashion Store',
  plan: 'professional',
  created_at: '2024-01-15T10:00:00Z',
  status: 'active'
};

export const currentUser: User = {
  id: 'user-456',
  tenant_id: 'tenant-123',
  email: 'admin@jordanfashion.com',
  role: 'admin',
  last_login: '2025-06-27T20:30:00Z',
  created_at: '2024-01-15T10:05:00Z'
};

export const catalogItems: CatalogItem[] = [
  {
    id: 'item-1',
    tenant_id: 'tenant-123',
    sku: 'JFS-DRS-001',
    name: 'فستان صيفي أنيق',
    price_jod: 85.00,
    media_url: '/images/dress-1.jpg',
    description: 'فستان صيفي مريح بألوان زاهية مناسب للمناسبات الصيفية',
    category: 'فساتين',
    stock_quantity: 15,
    extras: {
      colors: ['أزرق', 'وردي', 'أخضر'],
      sizes: ['S', 'M', 'L', 'XL'],
      material: 'قطن 100%'
    },
    created_at: '2024-02-01T10:00:00Z',
    updated_at: '2025-06-20T15:30:00Z'
  },
  {
    id: 'item-2',
    tenant_id: 'tenant-123',
    sku: 'JFS-TOP-002',
    name: 'بلوزة كاجوال عصرية',
    price_jod: 45.00,
    media_url: '/images/top-1.jpg',
    description: 'بلوزة كاجوال بتصميم عصري مناسبة للاستخدام اليومي',
    category: 'بلوزات',
    stock_quantity: 28,
    extras: {
      colors: ['أبيض', 'أسود', 'بيج'],
      sizes: ['S', 'M', 'L'],
      material: 'بوليستر وقطن'
    },
    created_at: '2024-02-05T10:00:00Z',
    updated_at: '2025-06-18T12:00:00Z'
  },
  {
    id: 'item-3',
    tenant_id: 'tenant-123',
    sku: 'JFS-ACC-003',
    name: 'حقيبة يد أنيقة',
    price_jod: 120.00,
    media_url: '/images/bag-1.jpg',
    description: 'حقيبة يد جلدية فاخرة بتصميم كلاسيكي أنيق',
    category: 'إكسسوارات',
    stock_quantity: 8,
    extras: {
      colors: ['بني', 'أسود', 'كريمي'],
      material: 'جلد طبيعي',
      dimensions: '30x25x15 سم'
    },
    created_at: '2024-02-10T10:00:00Z',
    updated_at: '2025-06-15T09:15:00Z'
  },
  {
    id: 'item-4',
    tenant_id: 'tenant-123',
    sku: 'JFS-DRS-004',
    name: 'فستان سهرة فاخر',
    price_jod: 250.00,
    media_url: '/images/evening-dress.jpg',
    description: 'فستان سهرة طويل بتطريز يدوي مناسب للمناسبات الخاصة',
    category: 'فساتين',
    stock_quantity: 5,
    extras: {
      colors: ['ذهبي', 'فضي', 'أحمر داكن'],
      sizes: ['S', 'M', 'L'],
      material: 'حرير وشيفون',
      occasion: 'سهرات وأفراح'
    },
    created_at: '2024-03-01T10:00:00Z',
    updated_at: '2025-06-10T14:20:00Z'
  },
  {
    id: 'item-5',
    tenant_id: 'tenant-123',
    sku: 'JFS-SHO-005',
    name: 'حذاء كعب عالي',
    price_jod: 95.00,
    media_url: '/images/heels-1.jpg',
    description: 'حذاء كعب عالي مريح بتصميم أنيق مناسب للعمل والمناسبات',
    category: 'أحذية',
    stock_quantity: 12,
    extras: {
      colors: ['أسود', 'بيج', 'أحمر'],
      sizes: ['36', '37', '38', '39', '40'],
      heel_height: '8 سم',
      material: 'جلد صناعي عالي الجودة'
    },
    created_at: '2024-03-05T10:00:00Z',
    updated_at: '2025-06-08T11:45:00Z'
  }
];

export const orders: Order[] = [
  {
    id: 'order-1',
    tenant_id: 'tenant-123',
    sku: 'JFS-DRS-001',
    qty: 2,
    customer: 'سارة أحمد',
    phone: '+962791234567',
    status: 'confirmed',
    total_amount: 170.00,
    delivery_address: 'عمان، الجبيهة، شارع الملكة رانيا',
    notes: 'يفضل التوصيل بعد الساعة 3 عصراً',
    created_at: '2025-06-26T14:30:00Z',
    updated_at: '2025-06-26T15:00:00Z'
  },
  {
    id: 'order-2',
    tenant_id: 'tenant-123',
    sku: 'JFS-ACC-003',
    qty: 1,
    customer: 'نور محمد',
    phone: '+962799876543',
    status: 'pending',
    total_amount: 120.00,
    delivery_address: 'الزرقاء، حي الأمير راشد',
    created_at: '2025-06-27T09:15:00Z',
    updated_at: '2025-06-27T09:15:00Z'
  },
  {
    id: 'order-3',
    tenant_id: 'tenant-123',
    sku: 'JFS-DRS-004',
    qty: 1,
    customer: 'ليلى خالد',
    phone: '+962785555432',
    status: 'shipped',
    total_amount: 250.00,
    delivery_address: 'إربد، منطقة الحصن',
    notes: 'هدية - يرجى التغليف الخاص',
    created_at: '2025-06-25T16:20:00Z',
    updated_at: '2025-06-27T10:30:00Z'
  },
  {
    id: 'order-4',
    tenant_id: 'tenant-123',
    sku: 'JFS-TOP-002',
    qty: 3,
    customer: 'فاطمة علي',
    phone: '+962777123456',
    status: 'delivered',
    total_amount: 135.00,
    delivery_address: 'عمان، وسط البلد',
    created_at: '2025-06-24T11:00:00Z',
    updated_at: '2025-06-26T16:45:00Z'
  }
];

export const conversations: Conversation[] = [
  {
    id: 'conv-1',
    tenant_id: 'tenant-123',
    sender: 'سارة أحمد',
    text: 'مرحبا، أريد معرفة إذا كان الفستان الأزرق متوفر بمقاس M؟',
    ts: '2025-06-27T21:30:00Z',
    tokens_in: 15,
    tokens_out: 0,
    message_type: 'incoming',
    ai_generated: false
  },
  {
    id: 'conv-2',
    tenant_id: 'tenant-123',
    sender: 'AI Assistant',
    text: 'أهلاً وسهلاً سارة! نعم، الفستان الصيفي الأنيق باللون الأزرق متوفر بمقاس M. سعره 85 دينار أردني. هل تودين معرفة المزيد من التفاصيل؟',
    ts: '2025-06-27T21:30:30Z',
    tokens_in: 0,
    tokens_out: 28,
    message_type: 'outgoing',
    ai_generated: true,
    context: { product_sku: 'JFS-DRS-001', color: 'أزرق', size: 'M' }
  },
  {
    id: 'conv-3',
    tenant_id: 'tenant-123',
    sender: 'سارة أحمد',
    text: 'ممتاز! أريد طلب قطعتين من هذا الفستان',
    ts: '2025-06-27T21:31:15Z',
    tokens_in: 8,
    tokens_out: 0,
    message_type: 'incoming',
    ai_generated: false
  },
  {
    id: 'conv-4',
    tenant_id: 'tenant-123',
    sender: 'AI Assistant',
    text: 'ممتاز! سأسجل لك طلب قطعتين من الفستان الصيفي الأنيق باللون الأزرق مقاس M. المجموع 170 دينار. أحتاج منك رقم الهاتف وعنوان التوصيل لإتمام الطلب.',
    ts: '2025-06-27T21:31:45Z',
    tokens_in: 0,
    tokens_out: 35,
    message_type: 'outgoing',
    ai_generated: true,
    context: { order_intent: true, sku: 'JFS-DRS-001', qty: 2, total: 170 }
  }
];

export const businessProfile: BusinessProfile = {
  tenant_id: 'tenant-123',
  yaml_profile: {
    business_name: 'Jordan Fashion Store',
    description: 'متجر أزياء نسائية عصرية يقدم أجمل التصاميم المناسبة للمرأة الأردنية',
    contact_info: {
      phone: '+962791234567',
      email: 'info@jordanfashion.com',
      address: 'عمان، الأردن - شارع الملكة رانيا'
    },
    operating_hours: {
      'الأحد': '10:00 - 22:00',
      'الاثنين': '10:00 - 22:00',
      'الثلاثاء': '10:00 - 22:00',
      'الأربعاء': '10:00 - 22:00',
      'الخميس': '10:00 - 22:00',
      'الجمعة': '14:00 - 22:00',
      'السبت': '10:00 - 22:00'
    },
    policies: {
      shipping: 'التوصيل مجاني للطلبات فوق 100 دينار داخل عمان، 5 دنانير خارج عمان',
      returns: 'إمكانية الاستبدال خلال 7 أيام من تاريخ الاستلام',
      payment: 'الدفع عند الاستلام أو تحويل بنكي'
    },
    ai_personality: {
      tone: 'ودود ومهني',
      language: 'العربية الأردنية',
      response_style: 'مفيد وسريع مع لمسة شخصية'
    }
  },
  created_at: '2024-01-15T10:10:00Z',
  updated_at: '2025-06-20T14:00:00Z'
};

export const kbDocuments: KBDocument[] = [
  {
    id: 'kb-1',
    tenant_id: 'tenant-123',
    file_uri: '/documents/sizing-guide.pdf',
    title: 'دليل المقاسات',
    vector_id: 'vec-001',
    content_preview: 'دليل شامل لمقاسات جميع المنتجات مع جدول تحويل المقاسات...',
    file_type: 'PDF',
    file_size: 2048000,
    created_at: '2024-02-01T10:00:00Z'
  },
  {
    id: 'kb-2',
    tenant_id: 'tenant-123',
    file_uri: '/documents/care-instructions.pdf',
    title: 'تعليمات العناية بالملابس',
    vector_id: 'vec-002',
    content_preview: 'إرشادات مفصلة للعناية بالأقمشة المختلفة وطرق الغسيل...',
    file_type: 'PDF',
    file_size: 1536000,
    created_at: '2024-02-05T10:00:00Z'
  },
  {
    id: 'kb-3',
    tenant_id: 'tenant-123',
    file_uri: '/documents/return-policy.md',
    title: 'سياسة الاستبدال والإرجاع',
    vector_id: 'vec-003',
    content_preview: 'شروط وأحكام استبدال وإرجاع المنتجات...',
    file_type: 'Markdown',
    file_size: 512000,
    created_at: '2024-02-10T10:00:00Z'
  }
];

export const usageStats: UsageStats[] = [
  {
    id: 'usage-1',
    tenant_id: 'tenant-123',
    date: '2025-06-27',
    openai_cost_usd: 12.45,
    meta_messages: 234,
    total_conversations: 67,
    orders_created: 8,
    customer_satisfaction: 4.8
  },
  {
    id: 'usage-2',
    tenant_id: 'tenant-123',
    date: '2025-06-26',
    openai_cost_usd: 15.30,
    meta_messages: 289,
    total_conversations: 78,
    orders_created: 12,
    customer_satisfaction: 4.7
  },
  {
    id: 'usage-3',
    tenant_id: 'tenant-123',
    date: '2025-06-25',
    openai_cost_usd: 18.75,
    meta_messages: 312,
    total_conversations: 89,
    orders_created: 15,
    customer_satisfaction: 4.9
  }
];

export const dashboardStats: DashboardStats = {
  total_conversations: 1523,
  active_orders: 28,
  revenue_this_month: 8750.00,
  ai_cost_this_month: 342.50,
  customer_satisfaction: 4.8,
  response_time_avg: 1.2,
  conversion_rate: 18.5,
  top_products: catalogItems.slice(0, 3),
  recent_orders: orders.slice(0, 4)
};
