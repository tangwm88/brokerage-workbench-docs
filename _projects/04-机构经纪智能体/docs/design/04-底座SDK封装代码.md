# 机构经纪员工端工作台 - 底座SDK封装代码

**版本**：v1.0  
**日期**：2026-03-06  
**语言**：TypeScript / Node.js

---

## 目录

1. [架构概述](#一架构概述)
2. [核心SDK设计](#二核心sdk设计)
3. [统一语料模块](#三统一语料模块)
4. [关系网络模块](#四关系网络模块)
5. [身份权限模块](#五身份权限模块)
6. [风控规则模块](#六风控规则模块)
7. [缓存与降级策略](#七缓存与降级策略)
8. [使用示例](#八使用示例)

---

## 一、架构概述

### 1.1 模块划分

```
BaseSDK/
├── core/
│   ├── BaseClient.ts          # 核心客户端
│   ├── AuthManager.ts         # 认证管理
│   └── RetryPolicy.ts         # 重试策略
├── modules/
│   ├── UnifiedCorpus.ts       # 统一语料
│   ├── RelationNetwork.ts     # 关系网络
│   ├── IdentityAuth.ts        # 身份权限
│   └── RiskControl.ts         # 风控规则
├── cache/
│   ├── CacheManager.ts        # 缓存管理
│   └── strategies/
│       ├── MemoryCache.ts
│       └── RedisCache.ts
├── types/
│   └── index.ts               # 类型定义
└── index.ts                   # 入口
```

### 1.2 配置结构

```typescript
interface BaseSDKConfig {
  // 底座服务端点
  baseUrl: string;
  
  // 认证配置
  auth: {
    appId: string;
    appSecret: string;
    tokenRefreshThreshold?: number; // 提前多久刷新token（秒），默认300
  };
  
  // 请求配置
  request: {
    timeout: number;              // 默认超时（毫秒）
    maxRetries: number;           // 最大重试次数
    retryDelay: number;           // 重试间隔（毫秒）
  };
  
  // 缓存配置
  cache: {
    enabled: boolean;
    defaultTTL: number;           // 默认缓存时间（秒）
    redis?: {
      host: string;
      port: number;
      password?: string;
    };
  };
  
  // 降级配置
  fallback: {
    enabled: boolean;             // 是否启用降级
    timeoutFallback: boolean;     // 超时时降级
    errorFallback: boolean;       // 错误时降级
  };
}
```

---

## 二、核心SDK设计

### 2.1 底座客户端 (BaseClient)

```typescript
// src/core/BaseClient.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { EventEmitter } from 'events';
import { AuthManager } from './AuthManager';
import { RetryPolicy } from './RetryPolicy';
import { CacheManager } from '../cache/CacheManager';
import { BaseSDKConfig, RequestOptions, BaseResponse } from '../types';

export class BaseClient extends EventEmitter {
  private httpClient: AxiosInstance;
  private authManager: AuthManager;
  private retryPolicy: RetryPolicy;
  private cacheManager: CacheManager;
  private config: BaseSDKConfig;

  constructor(config: BaseSDKConfig) {
    super();
    this.config = config;
    
    // 初始化HTTP客户端
    this.httpClient = axios.create({
      baseURL: config.baseUrl,
      timeout: config.request.timeout,
      headers: {
        'Content-Type': 'application/json',
        'X-App-Id': config.auth.appId,
        'X-Client-Version': '1.0.0'
      }
    });
    
    // 初始化各模块
    this.authManager = new AuthManager(config.auth, this.httpClient);
    this.retryPolicy = new RetryPolicy(config.request);
    this.cacheManager = new CacheManager(config.cache);
    
    // 设置拦截器
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加认证Token
    this.httpClient.interceptors.request.use(
      async (config) => {
        const token = await this.authManager.getValidToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器 - 处理错误和重试
    this.httpClient.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { retryCount?: number };
        
        // Token过期，刷新后重试
        if (error.response?.status === 401) {
          try {
            await this.authManager.refreshToken();
            return this.httpClient(originalRequest);
          } catch (refreshError) {
            this.emit('authError', refreshError);
            return Promise.reject(refreshError);
          }
        }
        
        // 可重试错误
        if (this.retryPolicy.shouldRetry(error, originalRequest.retryCount || 0)) {
          originalRequest.retryCount = (originalRequest.retryCount || 0) + 1;
          await this.retryPolicy.delay(originalRequest.retryCount);
          return this.httpClient(originalRequest);
        }
        
        return Promise.reject(error);
      }
    );
  }

  // 通用请求方法
  async request<T>(
    method: string,
    path: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    const cacheKey = `${method}:${path}:${JSON.stringify(data)}`;
    
    // 检查缓存
    if (options.cache !== false && this.config.cache.enabled) {
      const cached = await this.cacheManager.get<T>(cacheKey);
      if (cached) {
        this.emit('cacheHit', { path, cacheKey });
        return cached;
      }
    }

    try {
      const response = await this.httpClient.request<BaseResponse<T>>({
        method,
        url: path,
        data: ['POST', 'PUT', 'PATCH'].includes(method) ? data : undefined,
        params: ['GET', 'DELETE'].includes(method) ? data : undefined,
        timeout: options.timeout || this.config.request.timeout
      });

      const result = response.data.data;
      
      // 写入缓存
      if (options.cache !== false && this.config.cache.enabled) {
        const ttl = options.cacheTTL || this.config.cache.defaultTTL;
        await this.cacheManager.set(cacheKey, result, ttl);
      }
      
      return result;
    } catch (error) {
      // 降级处理
      if (this.config.fallback.enabled && options.fallback !== false) {
        const fallback = await this.handleFallback<T>(path, error);
        if (fallback !== undefined) {
          return fallback;
        }
      }
      throw error;
    }
  }

  // 降级处理
  private async handleFallback<T>(path: string, error: any): Promise<T | undefined> {
    // 记录降级日志
    this.emit('fallback', { path, error: error.message });
    
    // 根据路径返回默认数据
    const fallbacks: Record<string, any> = {
      '/corpus/entity': null,
      '/network/relations': [],
      '/auth/permissions': []
    };
    
    for (const [prefix, defaultValue] of Object.entries(fallbacks)) {
      if (path.startsWith(prefix)) {
        return defaultValue as T;
      }
    }
    
    return undefined;
  }

  // GET请求
  get<T>(path: string, params?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>('GET', path, params, options);
  }

  // POST请求
  post<T>(path: string, data?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>('POST', path, data, options);
  }

  // PUT请求
  put<T>(path: string, data?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>('PUT', path, data, options);
  }

  // DELETE请求
  delete<T>(path: string, params?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>('DELETE', path, params, options);
  }

  // 清除缓存
  async clearCache(pattern?: string) {
    await this.cacheManager.clear(pattern);
  }

  // 获取健康状态
  async health(): Promise<{ status: string; latency: number }> {
    const start = Date.now();
    try {
      await this.httpClient.get('/health');
      return { status: 'healthy', latency: Date.now() - start };
    } catch {
      return { status: 'unhealthy', latency: Date.now() - start };
    }
  }
}
```

### 2.2 认证管理器 (AuthManager)

```typescript
// src/core/AuthManager.ts
import { AxiosInstance } from 'axios';
import { AuthConfig, TokenInfo } from '../types';

export class AuthManager {
  private tokenInfo: TokenInfo | null = null;
  private refreshPromise: Promise<string> | null = null;

  constructor(
    private config: AuthConfig,
    private httpClient: AxiosInstance
  ) {}

  // 获取有效Token
  async getValidToken(): Promise<string | null> {
    // 检查当前token是否有效
    if (this.tokenInfo && !this.isTokenExpired()) {
      return this.tokenInfo.accessToken;
    }

    // 刷新token
    try {
      return await this.refreshToken();
    } catch (error) {
      // 刷新失败，尝试重新认证
      return await this.authenticate();
    }
  }

  // 检查token是否过期
  private isTokenExpired(): boolean {
    if (!this.tokenInfo) return true;
    
    const threshold = this.config.tokenRefreshThreshold || 300; // 默认5分钟
    const expiryTime = this.tokenInfo.expiresAt - threshold * 1000;
    return Date.now() >= expiryTime;
  }

  // 刷新Token
  async refreshToken(): Promise<string> {
    // 防止并发刷新
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.doRefresh();
    
    try {
      const token = await this.refreshPromise;
      return token;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async doRefresh(): Promise<string> {
    if (!this.tokenInfo?.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.httpClient.post('/auth/refresh', {
      refreshToken: this.tokenInfo.refreshToken
    });

    this.tokenInfo = {
      accessToken: response.data.data.accessToken,
      refreshToken: response.data.data.refreshToken,
      expiresAt: Date.now() + response.data.data.expiresIn * 1000
    };

    return this.tokenInfo.accessToken;
  }

  // 初始认证
  async authenticate(): Promise<string> {
    const response = await this.httpClient.post('/auth/token', {
      appId: this.config.appId,
      appSecret: this.config.appSecret,
      grantType: 'client_credentials'
    });

    this.tokenInfo = {
      accessToken: response.data.data.accessToken,
      refreshToken: response.data.data.refreshToken,
      expiresAt: Date.now() + response.data.data.expiresIn * 1000
    };

    return this.tokenInfo.accessToken;
  }

  // 清除Token
  clearToken() {
    this.tokenInfo = null;
    this.refreshPromise = null;
  }
}
```

### 2.3 重试策略 (RetryPolicy)

```typescript
// src/core/RetryPolicy.ts
import { AxiosError } from 'axios';
import { RequestConfig } from '../types';

export class RetryPolicy {
  constructor(private config: RequestConfig) {}

  // 判断是否应该重试
  shouldRetry(error: AxiosError, retryCount: number): boolean {
    // 超过最大重试次数
    if (retryCount >= this.config.maxRetries) {
      return false;
    }

    // 网络错误
    if (!error.response) {
      return true;
    }

    // 特定状态码重试
    const retryableStatuses = [408, 429, 500, 502, 503, 504];
    if (retryableStatuses.includes(error.response.status)) {
      return true;
    }

    return false;
  }

  // 延迟函数（指数退避）
  async delay(retryCount: number): Promise<void> {
    const baseDelay = this.config.retryDelay;
    const exponentialDelay = baseDelay * Math.pow(2, retryCount - 1);
    const jitter = Math.random() * 100; // 随机抖动
    
    await new Promise(resolve => setTimeout(resolve, exponentialDelay + jitter));
  }
}
```

### 2.4 缓存管理器 (CacheManager)

```typescript
// src/cache/CacheManager.ts
import { CacheConfig } from '../types';
import { MemoryCache } from './strategies/MemoryCache';
import { RedisCache } from './strategies/RedisCache';

interface CacheStrategy {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(pattern?: string): Promise<void>;
}

export class CacheManager {
  private strategy: CacheStrategy;

  constructor(config: CacheConfig) {
    if (config.redis) {
      this.strategy = new RedisCache(config.redis);
    } else {
      this.strategy = new MemoryCache();
    }
  }

  async get<T>(key: string): Promise<T | null> {
    return this.strategy.get<T>(key);
  }

  async set<T>(key: string, value: T, ttl: number): Promise<void> {
    await this.strategy.set(key, value, ttl);
  }

  async delete(key: string): Promise<void> {
    await this.strategy.delete(key);
  }

  async clear(pattern?: string): Promise<void> {
    await this.strategy.clear(pattern);
  }
}
```

```typescript
// src/cache/strategies/MemoryCache.ts
import NodeCache from 'node-cache';

export class MemoryCache {
  private cache: NodeCache;

  constructor() {
    this.cache = new NodeCache({
      stdTTL: 3600,
      checkperiod: 600
    });
  }

  async get<T>(key: string): Promise<T | null> {
    return this.cache.get<T>(key) || null;
  }

  async set<T>(key: string, value: T, ttl: number): Promise<void> {
    this.cache.set(key, value, ttl);
  }

  async delete(key: string): Promise<void> {
    this.cache.del(key);
  }

  async clear(pattern?: string): Promise<void> {
    if (pattern) {
      const keys = this.cache.keys().filter(k => k.includes(pattern));
      this.cache.del(keys);
    } else {
      this.cache.flushAll();
    }
  }
}
```

---

## 三、统一语料模块

### 3.1 统一语料客户端

```typescript
// src/modules/UnifiedCorpus.ts
import { BaseClient } from '../core/BaseClient';
import {
  EntitySearchParams,
  EntitySearchResult,
  EntityProfile,
  SentimentAnalysis,
  IndustryInfo
} from '../types/corpus';

export class UnifiedCorpus {
  constructor(private client: BaseClient) {}

  private readonly BASE_PATH = '/corpus/v1';

  /**
   * 实体搜索
   * 根据名称、统一代码等搜索企业实体
   */
  async searchEntities(params: EntitySearchParams): Promise<EntitySearchResult[]> {
    return this.client.post<EntitySearchResult[]>(
      `${this.BASE_PATH}/entity/search`,
      params,
      { cacheTTL: 3600 } // 缓存1小时
    );
  }

  /**
   * 获取实体详情
   */
  async getEntityProfile(
    entityType: string,
    entityId: string,
    unifiedCode?: string
  ): Promise<EntityProfile> {
    return this.client.get<EntityProfile>(
      `${this.BASE_PATH}/entity/${entityType}/${entityId}`,
      { unifiedCode },
      { cacheTTL: 7200 } // 缓存2小时
    );
  }

  /**
   * 批量获取实体
   */
  async batchGetEntities(entityIds: string[]): Promise<EntityProfile[]> {
    return this.client.post<EntityProfile[]>(
      `${this.BASE_PATH}/entity/batch`,
      { entityIds },
      { cacheTTL: 3600 }
    );
  }

  /**
   * 获取实体工商信息
   */
  async getBusinessInfo(unifiedCode: string): Promise<any> {
    return this.client.get(
      `${this.BASE_PATH}/business-info/${unifiedCode}`,
      {},
      { cacheTTL: 86400 } // 缓存24小时（工商信息变化较少）
    );
  }

  /**
   * 获取行业信息
   */
  async getIndustryInfo(industryCode: string): Promise<IndustryInfo> {
    return this.client.get<IndustryInfo>(
      `${this.BASE_PATH}/industry/${industryCode}`,
      {},
      { cacheTTL: 86400 * 7 } // 缓存7天
    );
  }

  /**
   * 舆情分析
   */
  async analyzeSentiment(
    entityName: string,
    days: number = 90
  ): Promise<SentimentAnalysis> {
    return this.client.get<SentimentAnalysis>(
      `${this.BASE_PATH}/sentiment`,
      { entityName, days },
      { cacheTTL: 3600 } // 缓存1小时
    );
  }

  /**
   * 获取舆情详情
   */
  async getSentimentDetails(
    entityName: string,
    params: {
      startDate?: string;
      endDate?: string;
      sentiment?: 'positive' | 'negative' | 'neutral';
      limit?: number;
    }
  ): Promise<any[]> {
    return this.client.get(
      `${this.BASE_PATH}/sentiment/details`,
      { entityName, ...params },
      { cacheTTL: 1800 }
    );
  }

  /**
   * 公告查询
   */
  async queryAnnouncements(params: {
    entityName?: string;
    unifiedCode?: string;
    types?: string[];
    startDate?: string;
    endDate?: string;
    limit?: number;
  }): Promise<any[]> {
    return this.client.post(
      `${this.BASE_PATH}/announcements`,
      params,
      { cacheTTL: 3600 }
    );
  }

  /**
   * 获取公司新闻
   */
  async getCompanyNews(
    entityName: string,
    days: number = 30
  ): Promise<any[]> {
    return this.client.get(
      `${this.BASE_PATH}/news`,
      { entityName, days },
      { cacheTTL: 1800 }
    );
  }
}
```

### 3.2 语料类型定义

```typescript
// src/types/corpus.ts

// 实体搜索参数
export interface EntitySearchParams {
  keyword?: string;
  unifiedCode?: string;
  entityType?: 'organization' | 'person' | 'product';
  industry?: string;
  region?: string;
  fuzzyMatch?: boolean;
  limit?: number;
}

// 实体搜索结果
export interface EntitySearchResult {
  id: string;
  name: string;
  unifiedCode?: string;
  entityType: string;
  industry?: string;
  region?: string;
  confidence: number;
  aliases?: string[];
  matchScore: number;
  source: string;
}

// 实体画像
export interface EntityProfile {
  id: string;
  name: string;
  unifiedCode?: string;
  entityType: string;
  
  // 工商信息
  businessInfo?: {
    legalPerson: string;
    registeredCapital: number;
    establishmentDate: string;
    businessStatus: string;
    industryCode: string;
    industryName: string;
    province: string;
    city: string;
    address: string;
    businessScope: string;
  };
  
  // 联系信息
  contactInfo?: {
    phone?: string;
    email?: string;
    website?: string;
  };
  
  // 风险信息
  riskInfo?: {
    isAbnormal: boolean;
    abnormalReasons?: string[];
    isExecuted: boolean;
    executedAmount?: number;
    isRestricted: boolean;
    litigationCount?: number;
  };
  
  // 关联信息
  relatedInfo?: {
    parentCompany?: string;
    subsidiaries?: string[];
    branches?: string[];
  };
  
  // 时间戳
  updatedAt: string;
  dataSource: string[];
}

// 舆情分析
export interface SentimentAnalysis {
  entityName: string;
  period: {
    startDate: string;
    endDate: string;
  };
  overview: {
    totalCount: number;
    positiveCount: number;
    negativeCount: number;
    neutralCount: number;
    score: number; // -1到1
  };
  trend: Array<{
    date: string;
    count: number;
    sentiment: number;
  }>;
  highlights: Array<{
    title: string;
    summary: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    source: string;
    publishTime: string;
    url?: string;
  }>;
  riskAlerts?: Array<{
    level: 'high' | 'medium' | 'low';
    type: string;
    description: string;
  }>;
}

// 行业信息
export interface IndustryInfo {
  code: string;
  name: string;
  parentCode?: string;
  level: number;
  description?: string;
  trends?: {
    growthRate: number;
    marketSize: number;
    forecast: string;
  };
  keyCompanies?: string[];
}
```

---

## 四、关系网络模块

### 4.1 关系网络客户端

```typescript
// src/modules/RelationNetwork.ts
import { BaseClient } from '../core/BaseClient';
import {
  RelationQueryParams,
  RelationResult,
  EntityGraph,
  InvestmentRelation,
  CooperationRelation,
  RelatedPartyResult
} from '../types/network';

export class RelationNetwork {
  constructor(private client: BaseClient) {}

  private readonly BASE_PATH = '/network/v1';

  /**
   * 查询实体关系
   */
  async queryRelations(params: RelationQueryParams): Promise<RelationResult[]> {
    return this.client.post<RelationResult[]>(
      `${this.BASE_PATH}/relations`,
      params,
      { cacheTTL: 3600 }
    );
  }

  /**
   * 获取实体图谱
   */
  async getEntityGraph(
    entityId: string,
    depth: number = 2
  ): Promise<EntityGraph> {
    return this.client.get<EntityGraph>(
      `${this.BASE_PATH}/graph/${entityId}`,
      { depth },
      { cacheTTL: 7200 }
    );
  }

  /**
   * 查询投资关系
   */
  async queryInvestmentRelations(
    entityId: string,
    direction: 'in' | 'out' | 'both' = 'both'
  ): Promise<InvestmentRelation[]> {
    return this.client.get<InvestmentRelation[]>(
      `${this.BASE_PATH}/investment/${entityId}`,
      { direction },
      { cacheTTL: 86400 }
    );
  }

  /**
   * 查询合作关系
   */
  async queryCooperationRelations(
    entityId: string
  ): Promise<CooperationRelation[]> {
    return this.client.get<CooperationRelation[]>(
      `${this.BASE_PATH}/cooperation/${entityId}`,
      {},
      { cacheTTL: 3600 }
    );
  }

  /**
   * 查找关联方
   * 用于关联交易检查
   */
  async findRelatedParties(
    entityId: string,
    options: {
      maxDepth?: number;
      minConfidence?: number;
      relationTypes?: string[];
    } = {}
  ): Promise<RelatedPartyResult> {
    return this.client.post<RelatedPartyResult>(
      `${this.BASE_PATH}/related-parties`,
      { entityId, ...options },
      { cacheTTL: 3600 }
    );
  }

  /**
   * 路径查询
   * 查找两个实体之间的关系路径
   */
  async findPath(
    fromEntityId: string,
    toEntityId: string,
    maxDepth: number = 3
  ): Promise<string[][]> {
    return this.client.post<string[][]>(
      `${this.BASE_PATH}/path`,
      { fromEntityId, toEntityId, maxDepth },
      { cacheTTL: 3600 }
    );
  }

  /**
   * 共同关联方
   */
  async findCommonRelations(
    entityIds: string[],
    relationType?: string
  ): Promise<Array<{
    entityId: string;
    entityName: string;
    relationTypes: string[];
  }>> {
    return this.client.post(
      `${this.BASE_PATH}/common-relations`,
      { entityIds, relationType },
      { cacheTTL: 3600 }
    );
  }

  /**
   * 客户查重（基于关系网络）
   */
  async checkDuplicateByNetwork(
    customerName: string,
    unifiedCode?: string
  ): Promise<{
    isDuplicate: boolean;
    confidence: number;
    matches: Array<{
      entityId: string;
      entityName: string;
      matchType: string;
      confidence: number;
    }>;
  }> {
    return this.client.post(
      `${this.BASE_PATH}/duplicate-check`,
      { customerName, unifiedCode },
      { cacheTTL: 1800 }
    );
  }
}
```

### 4.2 关系网络类型定义

```typescript
// src/types/network.ts

// 关系查询参数
export interface RelationQueryParams {
  entityId: string;
  entityType?: string;
  relationTypes?: string[];
  direction?: 'in' | 'out' | 'both';
  minConfidence?: number;
  limit?: number;
}

// 关系结果
export interface RelationResult {
  id: string;
  source: {
    id: string;
    name: string;
    type: string;
  };
  target: {
    id: string;
    name: string;
    type: string;
  };
  relationType: string;
  relationName: string;
  confidence: number;
  properties?: Record<string, any>;
  startTime?: string;
  endTime?: string;
  isActive: boolean;
  dataSource: string;
}

// 实体图谱
export interface EntityGraph {
  center: {
    id: string;
    name: string;
    type: string;
  };
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    properties?: Record<string, any>;
  }>;
  edges: Array<{
    source: string;
    target: string;
    relationType: string;
    confidence: number;
  }>;
  statistics: {
    totalNodes: number;
    totalEdges: number;
    nodeTypes: Record<string, number>;
    relationTypes: Record<string, number>;
  };
}

// 投资关系
export interface InvestmentRelation {
  id: string;
  investor: {
    id: string;
    name: string;
  };
  investee: {
    id: string;
    name: string;
  };
  amount?: number;
  ratio?: number;
  currency: string;
  investmentDate?: string;
  investmentRounds?: string;
  isControlling: boolean;
  dataSource: string;
}

// 合作关系
export interface CooperationRelation {
  id: string;
  parties: Array<{
    id: string;
    name: string;
  }>;
  cooperationType: string;
  startDate?: string;
  endDate?: string;
  isActive: boolean;
  description?: string;
  dataSource: string;
}

// 关联方结果
export interface RelatedPartyResult {
  entityId: string;
  entityName: string;
  relatedParties: Array<{
    entityId: string;
    entityName: string;
    relationType: string;
    relationPath: string[];
    confidence: number;
    distance: number;
  }>;
  totalCount: number;
  riskLevel: 'high' | 'medium' | 'low';
}
```

---

## 五、身份权限模块

### 5.1 身份权限客户端

```typescript
// src/modules/IdentityAuth.ts
import { BaseClient } from '../core/BaseClient';
import {
  UserIdentity,
  Permission,
  Role,
  Department,
  AuthCheckResult
} from '../types/identity';

export class IdentityAuth {
  constructor(private client: BaseClient) {}

  private readonly BASE_PATH = '/identity/v1';

  /**
   * 获取用户身份
   */
  async getUserIdentity(userId: string): Promise<UserIdentity> {
    return this.client.get<UserIdentity>(
      `${this.BASE_PATH}/users/${userId}`,
      {},
      { cacheTTL: 3600 }
    );
  }

  /**
   * 批量获取用户
   */
  async batchGetUsers(userIds: string[]): Promise<UserIdentity[]> {
    return this.client.post<UserIdentity[]>(
      `${this.BASE_PATH}/users/batch`,
      { userIds },
      { cacheTTL: 3600 }
    );
  }

  /**
   * 获取用户权限
   */
  async getUserPermissions(userId: string): Promise<Permission[]> {
    return this.client.get<Permission[]>(
      `${this.BASE_PATH}/users/${userId}/permissions`,
      {},
      { cacheTTL: 1800 }
    );
  }

  /**
   * 检查权限
   */
  async checkPermission(
    userId: string,
    permission: string
  ): Promise<AuthCheckResult> {
    return this.client.post<AuthCheckResult>(
      `${this.BASE_PATH}/check-permission`,
      { userId, permission },
      { cacheTTL: 300 } // 缓存5分钟
    );
  }

  /**
   * 批量检查权限
   */
  async batchCheckPermissions(
    userId: string,
    permissions: string[]
  ): Promise<Record<string, boolean>> {
    return this.client.post<Record<string, boolean>>(
      `${this.BASE_PATH}/check-permissions`,
      { userId, permissions },
      { cacheTTL: 300 }
    );
  }

  /**
   * 获取用户角色
   */
  async getUserRoles(userId: string): Promise<Role[]> {
    return this.client.get<Role[]>(
      `${this.BASE_PATH}/users/${userId}/roles`,
      {},
      { cacheTTL: 1800 }
    );
  }

  /**
   * 获取部门信息
   */
  async getDepartment(deptId: string): Promise<Department> {
    return this.client.get<Department>(
      `${this.BASE_PATH}/departments/${deptId}`,
      {},
      { cacheTTL: 86400 }
    );
  }

  /**
   * 获取部门成员
   */
  async getDepartmentMembers(
    deptId: string,
    recursive: boolean = false
  ): Promise<UserIdentity[]> {
    return this.client.get<UserIdentity[]>(
      `${this.BASE_PATH}/departments/${deptId}/members`,
      { recursive },
      { cacheTTL: 1800 }
    );
  }

  /**
   * 搜索用户
   */
  async searchUsers(params: {
    keyword?: string;
    departmentId?: string;
    roleId?: string;
    limit?: number;
  }): Promise<UserIdentity[]> {
    return this.client.get<UserIdentity[]>(
      `${this.BASE_PATH}/users/search`,
      params,
      { cacheTTL: 300 }
    );
  }

  /**
   * 获取组织架构
   */
  async getOrgStructure(rootDeptId?: string): Promise<Department> {
    return this.client.get<Department>(
      `${this.BASE_PATH}/org-structure`,
      { rootDeptId },
      { cacheTTL: 86400 }
    );
  }

  /**
   * 验证Token
   */
  async validateToken(token: string): Promise<{
    valid: boolean;
    userId?: string;
    expiresAt?: string;
  }> {
    return this.client.post(
      `${this.BASE_PATH}/validate-token`,
      { token },
      { cache: false }
    );
  }

  /**
   * 获取审批链
   */
  async getApprovalChain(params: {
    userId: string;
    approvalType: string;
    amount?: number;
  }): Promise<Array<{
    step: number;
    role: string;
    userId?: string;
    userName?: string;
    isRequired: boolean;
  }>> {
    return this.client.post(
      `${this.BASE_PATH}/approval-chain`,
      params,
      { cacheTTL: 1800 }
    );
  }
}
```

### 5.2 身份权限类型定义

```typescript
// src/types/identity.ts

// 用户身份
export interface UserIdentity {
  id: string;
  employeeNo: string;
  name: string;
  email: string;
  phone?: string;
  avatar?: string;
  
  // 组织信息
  department: {
    id: string;
    name: string;
    code: string;
    parentId?: string;
  };
  
  // 岗位信息
  position?: {
    id: string;
    name: string;
    level: number;
  };
  
  // 角色
  roles: Array<{
    id: string;
    name: string;
    code: string;
  }>;
  
  // 状态
  status: 'active' | 'inactive' | 'suspended';
  
  // 时间戳
  createdAt: string;
  updatedAt: string;
}

// 权限
export interface Permission {
  id: string;
  name: string;
  code: string;
  resource: string;
  action: string;
  description?: string;
}

// 角色
export interface Role {
  id: string;
  name: string;
  code: string;
  description?: string;
  permissions: Permission[];
}

// 部门
export interface Department {
  id: string;
  name: string;
  code: string;
  parentId?: string;
  managerId?: string;
  managerName?: string;
  children?: Department[];
  memberCount?: number;
}

// 权限检查结果
export interface AuthCheckResult {
  allowed: boolean;
  permission: string;
  reason?: string;
  constraints?: Array<{
    type: string;
    value: any;
  }>;
}
```

---

## 六、风控规则模块

### 6.1 风控规则客户端

```typescript
// src/modules/RiskControl.ts
import { BaseClient } from '../core/BaseClient';
import {
  BlacklistCheckResult,
  AMLRiskResult,
  SuitabilityCheckResult,
  ComplianceCheckResult,
  RiskAlert
} from '../types/risk';

export class RiskControl {
  constructor(private client: BaseClient) {}

  private readonly BASE_PATH = '/risk/v1';

  /**
   * 黑名单检查
   */
  async checkBlacklist(params: {
    name?: string;
    unifiedCode?: string;
    idNumber?: string;
    checkTypes?: string[];
  }): Promise<BlacklistCheckResult> {
    return this.client.post<BlacklistCheckResult>(
      `${this.BASE_PATH}/blacklist`,
      params,
      { cacheTTL: 3600 }
    );
  }

  /**
   * 反洗钱风险评估
   */
  async assessAMLRisk(params: {
    customerId?: string;
    name?: string;
    unifiedCode?: string;
    idNumber?: string;
  }): Promise<AMLRiskResult> {
    return this.client.post<AMLRiskResult>(
      `${this.BASE_PATH}/aml-risk`,
      params,
      { cacheTTL: 1800 }
    );
  }

  /**
   * 投资者适当性检查
   */
  async checkSuitability(params: {
    customerId: string;
    productRiskLevel: string;
    productType: string;
  }): Promise<SuitabilityCheckResult> {
    return this.client.post<SuitabilityCheckResult>(
      `${this.BASE_PATH}/suitability`,
      params,
      { cacheTTL: 300 }
    );
  }

  /**
   * 合规检查
   */
  async complianceCheck(params: {
    customerId?: string;
    checkItems: string[];
    businessType: string;
  }): Promise<ComplianceCheckResult> {
    return this.client.post<ComplianceCheckResult>(
      `${this.BASE_PATH}/compliance`,
      params,
      { cacheTTL: 300 }
    );
  }

  /**
   * 获取风险预警
   */
  async getRiskAlerts(params: {
    customerId?: string;
    alertTypes?: string[];
    severity?: string[];
    limit?: number;
  }): Promise<RiskAlert[]> {
    return this.client.get<RiskAlert[]>(
      `${this.BASE_PATH}/alerts`,
      params,
      { cacheTTL: 600 }
    );
  }

  /**
   * 关联交易检查
   */
  async checkRelatedPartyTransaction(params: {
    customerId: string;
    counterpartyId?: string;
    transactionType: string;
    amount?: number;
  }): Promise<{
    hasRelatedParty: boolean;
    relatedParties: Array<{
      entityId: string;
      entityName: string;
      relationType: string;
      requiresDisclosure: boolean;
    }>;
    requiresApproval: boolean;
    approvalLevel?: string;
  }> {
    return this.client.post(
      `${this.BASE_PATH}/related-party`,
      params,
      { cacheTTL: 600 }
    );
  }

  /**
   * 集中度风险检查
   */
  async checkConcentrationRisk(params: {
    customerId: string;
    position?: {
      assetType: string;
      amount: number;
    };
  }): Promise<{
    riskLevel: 'high' | 'medium' | 'low';
    concentrationRatio: number;
    warningThreshold: number;
    limitThreshold: number;
    warnings: string[];
  }> {
    return this.client.post(
      `${this.BASE_PATH}/concentration`,
      params,
      { cacheTTL: 300 }
    );
  }
}
```

### 6.2 风控类型定义

```typescript
// src/types/risk.ts

// 黑名单检查结果
export interface BlacklistCheckResult {
  isHit: boolean;
  hitType?: string;
  hitSource?: string;
  details?: Array<{
    listType: string;
    listName: string;
    hitReason: string;
    hitTime: string;
  }>;
  riskLevel: 'high' | 'medium' | 'low';
  suggestion: string;
}

// 反洗钱风险结果
export interface AMLRiskResult {
  riskLevel: 'high' | 'medium' | 'low';
  riskScore: number;
  factors: Array<{
    factor: string;
    weight: number;
    score: number;
  }>;
  watchlist?: {
    isOnWatchlist: boolean;
    watchlistType?: string;
  };
  unusualActivity?: Array<{
    type: string;
    description: string;
    severity: string;
  }>;
  requiresEnhancedDueDiligence: boolean;
  lastAssessmentDate: string;
}

// 适当性检查结果
export interface SuitabilityCheckResult {
  isSuitable: boolean;
  customerRiskLevel: string;
  productRiskLevel: string;
  matchScore: number;
  mismatches?: Array<{
    aspect: string;
    customerValue: string;
    productRequirement: string;
  }>;
  suggestion?: string;
}

// 合规检查结果
export interface ComplianceCheckResult {
  overallResult: 'pass' | 'fail' | 'conditional';
  items: Array<{
    itemCode: string;
    itemName: string;
    result: 'pass' | 'fail' | 'warning';
    message?: string;
    details?: any;
  }>;
  violations?: Array<{
    ruleCode: string;
    ruleName: string;
    severity: 'critical' | 'major' | 'minor';
    description: string;
  }>;
}

// 风险预警
export interface RiskAlert {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  customerId?: string;
  customerName?: string;
  triggeredAt: string;
  isAcknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  suggestedActions?: string[];
}
```

---

## 七、缓存与降级策略

### 7.1 缓存策略配置

```typescript
// src/config/cache-config.ts

export const CacheStrategies = {
  // 统一语料 - 工商信息（变化少，长期缓存）
  businessInfo: {
    ttl: 86400, // 24小时
    staleWhileRevalidate: true
  },
  
  // 统一语料 - 舆情（变化快，短期缓存）
  sentiment: {
    ttl: 1800, // 30分钟
    staleWhileRevalidate: true
  },
  
  // 关系网络 - 投资关系（相对稳定）
  investmentRelations: {
    ttl: 86400,
    staleWhileRevalidate: true
  },
  
  // 关系网络 - 合作关系（变化较快）
  cooperationRelations: {
    ttl: 3600, // 1小时
    staleWhileRevalidate: true
  },
  
  // 身份权限 - 用户信息
  userIdentity: {
    ttl: 3600,
    staleWhileRevalidate: true
  },
  
  // 身份权限 - 权限列表
  permissions: {
    ttl: 1800,
    staleWhileRevalidate: false
  },
  
  // 风控 - 黑名单
  blacklist: {
    ttl: 3600,
    staleWhileRevalidate: true
  },
  
  // 风控 - AML风险
  amlRisk: {
    ttl: 1800,
    staleWhileRevalidate: false
  }
};

// 缓存键生成器
export function generateCacheKey(
  module: string,
  method: string,
  params: Record<string, any>
): string {
  const sortedParams = Object.keys(params)
    .sort()
    .map(k => `${k}=${JSON.stringify(params[k])}`)
    .join('&');
  
  return `base:${module}:${method}:${Buffer.from(sortedParams).toString('base64')}`;
}
```

### 7.2 降级策略

```typescript
// src/config/fallback-config.ts

export const FallbackStrategies = {
  // 语料模块降级
  corpus: {
    enabled: true,
    timeout: 5000,
    defaults: {
      searchEntities: [],
      getEntityProfile: null,
      analyzeSentiment: {
        overview: { totalCount: 0, positiveCount: 0, negativeCount: 0, neutralCount: 0, score: 0 },
        trend: [],
        highlights: []
      }
    }
  },
  
  // 关系网络降级
  network: {
    enabled: true,
    timeout: 5000,
    defaults: {
      queryRelations: [],
      getEntityGraph: { center: null, nodes: [], edges: [], statistics: { totalNodes: 0, totalEdges: 0, nodeTypes: {}, relationTypes: {} } },
      findRelatedParties: { entityId: '', entityName: '', relatedParties: [], totalCount: 0, riskLevel: 'low' }
    }
  },
  
  // 身份权限降级
  identity: {
    enabled: true,
    timeout: 3000,
    defaults: {
      getUserIdentity: null,
      checkPermission: { allowed: false, permission: '', reason: '服务不可用' }
    }
  },
  
  // 风控降级（关键模块，默认拒绝）
  risk: {
    enabled: true,
    timeout: 3000,
    defaults: {
      checkBlacklist: { isHit: false, hitType: undefined, riskLevel: 'low', suggestion: '检查服务暂时不可用，请稍后重试或人工核实' },
      assessAMLRisk: { riskLevel: 'medium', riskScore: 50, factors: [], requiresEnhancedDueDiligence: true, lastAssessmentDate: new Date().toISOString() },
      checkSuitability: { isSuitable: false, customerRiskLevel: '', productRiskLevel: '', matchScore: 0, suggestion: '适当性检查服务暂时不可用' }
    }
  }
};

// 熔断器配置
export const CircuitBreakerConfig = {
  failureThreshold: 5,      // 失败阈值
  successThreshold: 3,      // 恢复成功阈值
  timeout: 60000,           // 熔断持续时间（毫秒）
  halfOpenRequests: 3       // 半开状态允许的请求数
};
```

---

## 八、使用示例

### 8.1 初始化SDK

```typescript
// src/sdk-instance.ts
import { BaseClient } from './core/BaseClient';
import { UnifiedCorpus } from './modules/UnifiedCorpus';
import { RelationNetwork } from './modules/RelationNetwork';
import { IdentityAuth } from './modules/IdentityAuth';
import { RiskControl } from './modules/RiskControl';

// 配置
const config = {
  baseUrl: process.env.BASE_API_URL || 'https://base.company.com',
  auth: {
    appId: process.env.BASE_APP_ID || '',
    appSecret: process.env.BASE_APP_SECRET || '',
    tokenRefreshThreshold: 300
  },
  request: {
    timeout: 10000,
    maxRetries: 3,
    retryDelay: 1000
  },
  cache: {
    enabled: true,
    defaultTTL: 3600,
    redis: process.env.REDIS_URL ? {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    } : undefined
  },
  fallback: {
    enabled: true,
    timeoutFallback: true,
    errorFallback: true
  }
};

// 创建客户端实例
const baseClient = new BaseClient(config);

// 导出各模块
export const baseSDK = {
  client: baseClient,
  corpus: new UnifiedCorpus(baseClient),
  network: new RelationNetwork(baseClient),
  identity: new IdentityAuth(baseClient),
  risk: new RiskControl(baseClient)
};

// 事件监听
baseClient.on('authError', (error) => {
  console.error('底座认证失败:', error);
  // 发送告警
});

baseClient.on('fallback', ({ path, error }) => {
  console.warn(`底座接口降级: ${path}`, error);
  // 记录降级日志
});

baseClient.on('cacheHit', ({ path, cacheKey }) => {
  console.debug(`缓存命中: ${path}`);
});
```

### 8.2 客户查重示例

```typescript
// 客户查重服务
import { baseSDK } from './sdk-instance';

export async function checkCustomerDuplicate(
  customerName: string,
  unifiedCode?: string
) {
  // 1. 调用底座关系网络查重
  const networkResult = await baseSDK.network.checkDuplicateByNetwork(
    customerName,
    unifiedCode
  );
  
  // 2. 调用语料搜索补充
  const corpusResult = await baseSDK.corpus.searchEntities({
    keyword: customerName,
    unifiedCode,
    fuzzyMatch: true,
    limit: 10
  });
  
  // 3. 合并结果
  const allMatches = [
    ...networkResult.matches.map(m => ({
      ...m,
      source: 'network'
    })),
    ...corpusResult.map(r => ({
      entityId: r.id,
      entityName: r.name,
      matchType: 'name_similarity',
      confidence: r.matchScore,
      source: 'corpus'
    }))
  ];
  
  // 4. 去重（按entityId）
  const uniqueMatches = Array.from(
    new Map(allMatches.map(m => [m.entityId, m])).values()
  );
  
  // 5. 排序（按置信度）
  uniqueMatches.sort((a, b) => b.confidence - a.confidence);
  
  return {
    isDuplicate: networkResult.isDuplicate,
    confidence: Math.max(networkResult.confidence, corpusResult[0]?.matchScore || 0),
    similarCustomers: uniqueMatches.slice(0, 5)
  };
}
```

### 8.3 开户预审示例

```typescript
// 开户预审服务
import { baseSDK } from './sdk-instance';

export async function preCheckAccountOpening(
  customerId: string,
  formData: any
) {
  const checks = await Promise.all([
    // 1. 黑名单检查
    baseSDK.risk.checkBlacklist({
      name: formData.customerName,
      unifiedCode: formData.unifiedCode
    }),
    
    // 2. 反洗钱风险评估
    baseSDK.risk.assessAMLRisk({
      customerId,
      name: formData.customerName,
      unifiedCode: formData.unifiedCode
    }),
    
    // 3. 适当性检查
    baseSDK.risk.checkSuitability({
      customerId,
      productRiskLevel: formData.productRiskLevel,
      productType: formData.accountType
    }),
    
    // 4. 关联交易检查
    baseSDK.risk.checkRelatedPartyTransaction({
      customerId,
      transactionType: 'account_opening'
    })
  ]);
  
  const [blacklist, aml, suitability, relatedParty] = checks;
  
  // 5. 计算综合得分
  let score = 100;
  const riskAlerts = [];
  
  if (blacklist.isHit) {
    score -= 50;
    riskAlerts.push({
      level: 'critical',
      type: 'blacklist',
      message: blacklist.suggestion
    });
  }
  
  if (aml.riskLevel === 'high') {
    score -= 20;
    riskAlerts.push({
      level: 'warning',
      type: 'aml',
      message: '反洗钱风险等级较高，需人工复核'
    });
  }
  
  if (!suitability.isSuitable) {
    score -= 15;
    riskAlerts.push({
      level: 'warning',
      type: 'suitability',
      message: suitability.suggestion
    });
  }
  
  if (relatedParty.hasRelatedParty) {
    riskAlerts.push({
      level: 'info',
      type: 'related_party',
      message: `发现${relatedParty.relatedParties.length}个关联方`
    });
  }
  
  // 6. 确定结果
  let result: 'pass' | 'conditional_pass' | 'fail' = 'pass';
  if (score < 50 || blacklist.isHit) {
    result = 'fail';
  } else if (score < 80) {
    result = 'conditional_pass';
  }
  
  return {
    checkResult: result,
    score,
    riskAlerts,
    details: { blacklist, aml, suitability, relatedParty }
  };
}
```

### 8.4 AI画像生成示例

```typescript
// AI画像生成服务
import { baseSDK } from './sdk-instance';

export async function generateCustomerProfile(
  customerId: string,
  customerName: string,
  unifiedCode?: string
) {
  // 1. 获取实体信息
  const entityInfo = await baseSDK.corpus.getEntityProfile(
    'organization',
    customerId,
    unifiedCode
  );
  
  // 2. 获取关系网络
  const relations = await baseSDK.network.queryInvestmentRelations(customerId);
  
  // 3. 获取舆情分析
  const sentiment = await baseSDK.corpus.analyzeSentiment(customerName, 90);
  
  // 4. 获取风险信息
  const riskAlerts = await baseSDK.risk.getRiskAlerts({ customerId });
  
  // 5. 整合画像（实际中可能还需要调用大模型进行推理）
  const profile = {
    basicInfo: {
      industry: entityInfo.businessInfo?.industryName,
      scale: categorizeScale(entityInfo.businessInfo?.registeredCapital),
      region: entityInfo.businessInfo?.province,
      establishedYears: calculateYears(entityInfo.businessInfo?.establishmentDate)
    },
    riskAssessment: {
      overallRisk: assessOverallRisk(entityInfo.riskInfo, sentiment, riskAlerts),
      complianceHistory: entityInfo.riskInfo?.isAbnormal ? '有异常' : '良好',
      creditRating: 'AA' // 可根据实际规则计算
    },
    dataSources: ['工商信息', '关系网络', '舆情数据', '风控系统']
  };
  
  return profile;
}

function categorizeScale(capital?: number): string {
  if (!capital) return '未知';
  if (capital >= 100000000) return '大型';
  if (capital >= 10000000) return '中型';
  return '小型';
}

function calculateYears(date?: string): number | null {
  if (!date) return null;
  return Math.floor((Date.now() - new Date(date).getTime()) / (365 * 24 * 60 * 60 * 1000));
}

function assessOverallRisk(
  riskInfo?: any,
  sentiment?: any,
  alerts?: any[]
): string {
  if (riskInfo?.isAbnormal || alerts?.some(a => a.severity === 'critical')) {
    return '高';
  }
  if (sentiment?.overview?.score < -0.3) {
    return '中高';
  }
  return '中';
}
```

---

*文档版本：v1.0*  
*最后更新：2026-03-06*