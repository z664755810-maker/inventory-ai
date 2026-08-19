const API_BASE_URL = '/api';

const api = {
    async request(url, method = 'GET', data = null) {
        const options = {
            method: method,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${url}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    },

    login(username, password) {
        return this.request('/login', 'POST', { username, password });
    },

    getCurrentUser() {
        return this.request('/current-user');
    },

    logout() {
        return this.request('/logout', 'POST');
    },

    // 用户管理
    getUsers() {
        return this.request('/users');
    },

    getUser(id) {
        return this.request(`/users/${id}`);
    },

    createUser(data) {
        return this.request('/users', 'POST', data);
    },

    // 注册
    register(username, password) {
        return this.request('/users', 'POST', { username, password });
    },

    // 忘记密码
    forgotPassword(username, newPassword) {
        return this.request('/forgot-password', 'POST', { username, newPassword });
    },

    updateUser(id, data) {
        return this.request(`/users/${id}`, 'PUT', data);
    },

    deleteUser(id) {
        return this.request(`/users/${id}`, 'DELETE');
    },

    // 商品类型
    getCategories() {
        return this.request('/categories');
    },

    getCategoryTree() {
        return this.request('/categories/tree');
    },

    getCategory(id) {
        return this.request(`/categories/${id}`);
    },

    createCategory(data) {
        return this.request('/categories', 'POST', data);
    },

    updateCategory(id, data) {
        return this.request(`/categories/${id}`, 'PUT', data);
    },

    deleteCategory(id) {
        return this.request(`/categories/${id}`, 'DELETE');
    },

    // 商品档案
    getProducts() {
        return this.request('/products');
    },

    getProduct(id) {
        return this.request(`/products/${id}`);
    },

    createProduct(data) {
        return this.request('/products', 'POST', data);
    },

    updateProduct(id, data) {
        return this.request(`/products/${id}`, 'PUT', data);
    },

    deleteProduct(id) {
        return this.request(`/products/${id}`, 'DELETE');
    },

    // 客户档案
    getCustomers() {
        return this.request('/customers');
    },

    getCustomer(id) {
        return this.request(`/customers/${id}`);
    },

    createCustomer(data) {
        return this.request('/customers', 'POST', data);
    },

    updateCustomer(id, data) {
        return this.request(`/customers/${id}`, 'PUT', data);
    },

    deleteCustomer(id) {
        return this.request(`/customers/${id}`, 'DELETE');
    },

    // 采购入库单
    getPurchaseOrders(days = null) {
        const url = days ? `/purchase-orders?days=${days}` : '/purchase-orders';
        return this.request(url);
    },

    getPurchaseOrder(id) {
        return this.request(`/purchase-orders/${id}`);
    },

    createPurchaseOrder(data) {
        return this.request('/purchase-orders', 'POST', data);
    },

    updatePurchaseOrder(id, data) {
        return this.request(`/purchase-orders/${id}`, 'PUT', data);
    },

    deletePurchaseOrder(id) {
        return this.request(`/purchase-orders/${id}`, 'DELETE');
    },

    // 销售出库单
    getSalesOrders(days = null) {
        const url = days ? `/sales-orders?days=${days}` : '/sales-orders';
        return this.request(url);
    },

    getSalesOrder(id) {
        return this.request(`/sales-orders/${id}`);
    },

    createSalesOrder(data) {
        return this.request('/sales-orders', 'POST', data);
    },

    updateSalesOrder(id, data) {
        return this.request(`/sales-orders/${id}`, 'PUT', data);
    },

    deleteSalesOrder(id) {
        return this.request(`/sales-orders/${id}`, 'DELETE');
    },

    // 库存查询
    getStock() {
        return this.request('/stock');
    },

    getStockByProduct(productId) {
        return this.request(`/stock/${productId}`);
    },

    // 发票管理
    getInvoices() {
        return this.request('/invoices');
    },

    getInvoice(id) {
        return this.request(`/invoices/${id}`);
    },

    createInvoice(data) {
        return this.request('/invoices', 'POST', data);
    },

    updateInvoice(id, data) {
        return this.request(`/invoices/${id}`, 'PUT', data);
    },

    deleteInvoice(id) {
        return this.request(`/invoices/${id}`, 'DELETE');
    },

    // AI智能体
    queryAgent(agentType, message) {
        return this.request('/agent/query', 'POST', { agent_type: agentType, message: message });
    },

    getAgentConfigs() {
        return this.request('/agent/configs');
    }
};
