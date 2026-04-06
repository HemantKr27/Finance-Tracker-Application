const apiBase = "/api/v1";

const state = {
    token: localStorage.getItem("finance_token") || "",
    accounts: [],
    categories: [],
    transactions: [],
    budgets: [],
};

const elements = {
    apiStatus: document.getElementById("apiStatus"),
    tokenPreview: document.getElementById("tokenPreview"),
    totalBalance: document.getElementById("totalBalance"),
    totalIncome: document.getElementById("totalIncome"),
    totalExpense: document.getElementById("totalExpense"),
    budgetsCount: document.getElementById("budgetsCount"),
    budgetHealth: document.getElementById("budgetHealth"),
    snapshotBalance: document.getElementById("snapshotBalance"),
    snapshotIncome: document.getElementById("snapshotIncome"),
    snapshotExpense: document.getElementById("snapshotExpense"),
    snapshotNetFlow: document.getElementById("snapshotNetFlow"),
    accountsCount: document.getElementById("accountsCount"),
    transactionsCount: document.getElementById("transactionsCount"),
    plannedBudgetAmount: document.getElementById("plannedBudgetAmount"),
    spentBudgetAmount: document.getElementById("spentBudgetAmount"),
    remainingBudgetAmount: document.getElementById("remainingBudgetAmount"),
    budgetUsageAverage: document.getElementById("budgetUsageAverage"),
    categoryPieChart: document.getElementById("categoryPieChart"),
    monthlySpendingChart: document.getElementById("monthlySpendingChart"),
    incomeExpenseChart: document.getElementById("incomeExpenseChart"),
    accountsList: document.getElementById("accountsList"),
    categoriesList: document.getElementById("categoriesList"),
    budgetsList: document.getElementById("budgetsList"),
    transactionsTable: document.getElementById("transactionsTable"),
    activityLog: document.getElementById("activityLog"),
    transAccount: document.getElementById("trans_account"),
    transCategory: document.getElementById("trans_category"),
    transTypeDisplay: document.getElementById("trans_type_display"),
    budgetCategoryHint: document.getElementById("budgetCategoryHint"),
    budgetForm: document.getElementById("budgetForm"),
    budgetCategoryRows: document.getElementById("budgetCategoriesRows"),
    addBudgetCategoryBtn: document.getElementById("addBudgetCategoryBtn"),
    refreshAllBtn: document.getElementById("refreshAllBtn"),
    logoutBtn: document.getElementById("logoutBtn"),
};

document.getElementById("registerForm").addEventListener("submit", handleRegister);
document.getElementById("loginForm").addEventListener("submit", handleLogin);
document.getElementById("accountForm").addEventListener("submit", handleAccountCreate);
document.getElementById("categoryForm").addEventListener("submit", handleCategoryCreate);
document.getElementById("transactionForm").addEventListener("submit", handleTransactionCreate);
document.getElementById("budgetForm").addEventListener("submit", handleBudgetCreate);
elements.refreshAllBtn.addEventListener("click", refreshDashboard);
elements.logoutBtn.addEventListener("click", logout);
elements.addBudgetCategoryBtn.addEventListener("click", () => addBudgetCategoryRow());
elements.budgetCategoryRows.addEventListener("click", handleBudgetCategoryRowActions);
elements.transCategory.addEventListener("change", syncTransactionTypeFromCategory);

bootstrap();

async function bootstrap() {
    updateSessionUI();
    await checkApi();
    if (state.token) {
        await refreshDashboard();
    } else {
        renderEmptyState();
        syncBudgetCategoryRows();
    }
}

async function checkApi() {
    try {
        const response = await fetch("/health");
        if (!response.ok) {
            throw new Error("Health check failed");
        }
        elements.apiStatus.textContent = "API online";
        elements.apiStatus.dataset.status = "online";
    } catch (error) {
        elements.apiStatus.textContent = "API unavailable";
        elements.apiStatus.dataset.status = "offline";
        logActivity("API check failed", error.message);
    }
}

function authHeaders(json = true) {
    const headers = {};
    if (json) {
        headers["Content-Type"] = "application/json";
    }
    if (state.token) {
        headers.Authorization = `Bearer ${state.token}`;
    }
    return headers;
}

async function request(path, options = {}) {
    const response = await fetch(`${apiBase}${path}`, options);
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
        const detail = payload?.detail || payload || "Request failed";
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    return payload;
}

async function handleRegister(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());

    try {
        const data = await request("/auth/register", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        logActivity("Registration successful", data);
        event.currentTarget.reset();
    } catch (error) {
        logActivity("Registration failed", error.message);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    try {
        const data = await request("/auth/login", {
            method: "POST",
            body: new URLSearchParams({
                username: formData.get("email"),
                password: formData.get("password"),
            }),
        });

        state.token = data.access_token;
        localStorage.setItem("finance_token", state.token);
        updateSessionUI();
        logActivity("Login successful", { token_type: data.token_type });
        await refreshDashboard();
    } catch (error) {
        logActivity("Login failed", error.message);
    }
}

async function handleAccountCreate(event) {
    event.preventDefault();
    if (!requireAuth()) {
        return;
    }

    const formData = new FormData(event.currentTarget);
    const payload = {
        name: formData.get("name"),
        type: formData.get("type"),
        balance: formData.get("balance"),
    };

    try {
        const data = await request("/accounts/", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        logActivity("Account created", data);
        event.currentTarget.reset();
        await refreshDashboard();
    } catch (error) {
        logActivity("Account creation failed", error.message);
    }
}

async function handleCategoryCreate(event) {
    event.preventDefault();
    if (!requireAuth()) {
        return;
    }

    const formData = new FormData(event.currentTarget);
    const payload = Object.fromEntries(formData.entries());

    try {
        const data = await request("/categories/", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        logActivity("Category created", data);
        event.currentTarget.reset();
        await refreshDashboard();
    } catch (error) {
        logActivity("Category creation failed", error.message);
    }
}

async function handleTransactionCreate(event) {
    event.preventDefault();
    if (!requireAuth()) {
        return;
    }

    const formData = new FormData(event.currentTarget);
    const payload = {
        account_id: Number(formData.get("account_id")),
        category_id: Number(formData.get("category_id")),
        amount: formData.get("amount"),
        description: formData.get("description") || null,
    };

    try {
        const data = await request("/transactions/", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        logActivity("Transaction created", data);
        event.currentTarget.reset();
        await refreshDashboard();
    } catch (error) {
        logActivity("Transaction creation failed", error.message);
    }
}

async function handleBudgetCreate(event) {
    event.preventDefault();
    if (!requireAuth()) {
        return;
    }

    const form = event.currentTarget;
    const formData = new FormData(form);
    const categoryRows = Array.from(elements.budgetCategoryRows.querySelectorAll(".allocation-row"));
    const categories = categoryRows
        .map((row) => ({
            category_id: Number(row.querySelector('[name="budget_category_id"]').value),
            allocated_amount: row.querySelector('[name="allocated_amount"]').value,
            alert_percentage: Number(row.querySelector('[name="alert_percentage"]').value || 80),
        }))
        .filter((item) => Number.isFinite(item.category_id) && item.category_id > 0 && item.allocated_amount);

    if (!categories.length) {
        logActivity("Budget creation failed", "Add at least one category allocation.");
        return;
    }

    const payload = {
        name: formData.get("name"),
        period: formData.get("period"),
        start_date: formData.get("start_date"),
        end_date: formData.get("end_date"),
        threshold_percentage: Number(formData.get("threshold_percentage")),
        is_recurring: formData.get("is_recurring") === "on",
        status: "active",
        categories,
    };

    try {
        const data = await request("/budgets/", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        logActivity("Budget created", data);
        form.reset();
        elements.budgetCategoryRows.innerHTML = "";
        addBudgetCategoryRow();
        await refreshDashboard();
    } catch (error) {
        logActivity("Budget creation failed", error.message);
    }
}

async function refreshDashboard() {
    if (!requireAuth()) {
        renderEmptyState();
        return;
    }

    try {
        const [accounts, categories, transactions, budgets] = await Promise.all([
            request("/accounts/", { headers: authHeaders(false) }),
            request("/categories/", { headers: authHeaders(false) }),
            request("/transactions/", { headers: authHeaders(false) }),
            request("/budgets/", { headers: authHeaders(false) }),
        ]);

        state.accounts = accounts;
        state.categories = categories;
        state.transactions = transactions;
        state.budgets = budgets;

        renderDashboard();
        logActivity("Dashboard refreshed", {
            accounts: accounts.length,
            categories: categories.length,
            transactions: transactions.length,
            budgets: budgets.length,
        });
    } catch (error) {
        logActivity("Dashboard refresh failed", error.message);
    }
}

function renderDashboard() {
    updateSummary();
    renderAnalytics();
    renderAccounts();
    renderCategories();
    renderBudgets();
    renderTransactions();
    fillTransactionSelects();
    syncTransactionTypeFromCategory();
    syncBudgetCategoryRows();
}

function renderEmptyState() {
    state.accounts = [];
    state.categories = [];
    state.transactions = [];
    state.budgets = [];
    updateSummary();
    renderAnalytics();
    renderAccounts();
    renderCategories();
    renderBudgets();
    renderTransactions();
    fillTransactionSelects();
    syncTransactionTypeFromCategory();
    syncBudgetCategoryRows();
}

function updateSummary() {
    const totalBalance = state.accounts.reduce((sum, account) => sum + Number(account.balance), 0);
    const totalIncome = state.transactions
        .filter((transaction) => transaction.type === "income")
        .reduce((sum, transaction) => sum + Number(transaction.amount), 0);
    const totalExpense = state.transactions
        .filter((transaction) => transaction.type === "expense")
        .reduce((sum, transaction) => sum + Number(transaction.amount), 0);
    const totalBudget = state.budgets.reduce((sum, budget) => sum + Number(budget.amount), 0);
    const spentBudget = state.budgets.reduce((sum, budget) => sum + Number(budget.spent_amount), 0);
    const remainingBudget = state.budgets.reduce((sum, budget) => sum + Number(budget.remaining_amount), 0);
    const averageUsage = state.budgets.length
        ? state.budgets.reduce((sum, budget) => sum + Number(budget.usage_percentage || 0), 0) / state.budgets.length
        : 0;

    elements.totalBalance.textContent = formatCurrency(totalBalance);
    elements.totalIncome.textContent = formatCurrency(totalIncome);
    elements.totalExpense.textContent = formatCurrency(totalExpense);
    elements.snapshotBalance.textContent = formatCurrency(totalBalance);
    elements.snapshotIncome.textContent = formatCurrency(totalIncome);
    elements.snapshotExpense.textContent = formatCurrency(totalExpense);
    elements.snapshotNetFlow.textContent = `Net flow: ${formatCurrency(totalIncome - totalExpense)}`;
    elements.accountsCount.textContent = String(state.accounts.length);
    elements.accountsCount.textContent += state.accounts.length === 1 ? " account connected" : " accounts connected";
    elements.transactionsCount.textContent = `${state.transactions.length} transactions tracked`;
    elements.budgetsCount.textContent = String(state.budgets.length);
    elements.budgetHealth.textContent = state.budgets.length
        ? "Budget tracking is live."
        : "No budgets yet. Create your first one below.";
    elements.plannedBudgetAmount.textContent = formatCurrency(totalBudget);
    elements.spentBudgetAmount.textContent = formatCurrency(spentBudget);
    elements.remainingBudgetAmount.textContent = formatCurrency(remainingBudget);
    elements.budgetUsageAverage.textContent = `${averageUsage.toFixed(1)}%`;
}

function renderAnalytics() {
    renderCategoryPieChart();
    renderMonthlySpendingChart();
    renderIncomeExpenseChart();
}

function renderCategoryPieChart() {
    const expenseByCategory = aggregateExpenseByCategory();
    const entries = Array.from(expenseByCategory.entries()).sort((left, right) => right[1] - left[1]);

    if (!entries.length) {
        elements.categoryPieChart.innerHTML = '<p class="empty-state">No expense data yet for category insights.</p>';
        return;
    }

    const total = entries.reduce((sum, [, value]) => sum + value, 0);
    let startAngle = -Math.PI / 2;
    const radius = 84;
    const center = 110;

    const slices = entries.map(([label, value], index) => {
        const portion = value / total;
        const endAngle = startAngle + portion * Math.PI * 2;
        const path = describeArc(center, center, radius, startAngle, endAngle);
        const color = chartColor(index);
        startAngle = endAngle;
        return `<path d="${path}" fill="${color}"></path>`;
    }).join("");

    const legend = entries.map(([label, value], index) => `
        <li>
            <span class="legend-swatch" style="background:${chartColor(index)}"></span>
            <span>${escapeHtml(label)}</span>
            <strong>${formatCurrency(value)}</strong>
        </li>
    `).join("");

    elements.categoryPieChart.innerHTML = `
        <div class="chart-layout">
            <svg class="pie-svg" viewBox="0 0 220 220" role="img" aria-label="Expense by category">
                ${slices}
                <circle cx="110" cy="110" r="44" fill="#fffaf2"></circle>
                <text x="110" y="105" text-anchor="middle" class="chart-center-label">Spent</text>
                <text x="110" y="125" text-anchor="middle" class="chart-center-value">${escapeHtml(compactCurrency(total))}</text>
            </svg>
            <ul class="chart-legend">${legend}</ul>
        </div>
    `;
}

function renderMonthlySpendingChart() {
    const monthlyExpense = aggregateMonthlyTotals("expense");
    const entries = Array.from(monthlyExpense.entries());

    if (!entries.length) {
        elements.monthlySpendingChart.innerHTML = '<p class="empty-state">No expense history yet for the monthly line chart.</p>';
        return;
    }

    const points = buildLinePoints(entries.map(([, value]) => value), 560, 240);
    const labels = entries.map(([label]) => label);

    elements.monthlySpendingChart.innerHTML = renderSvgChart({
        width: 560,
        height: 240,
        lines: [
            {
                color: "#db5f36",
                points,
                area: true,
            },
        ],
        labels,
        values: entries.map(([, value]) => value),
        title: "Monthly spending trend",
    });
}

function renderIncomeExpenseChart() {
    const incomeMap = aggregateMonthlyTotals("income");
    const expenseMap = aggregateMonthlyTotals("expense");
    const labels = Array.from(new Set([...incomeMap.keys(), ...expenseMap.keys()]));

    if (!labels.length) {
        elements.incomeExpenseChart.innerHTML = '<p class="empty-state">No transactions yet for the income vs expense chart.</p>';
        return;
    }

    const incomeValues = labels.map((label) => incomeMap.get(label) || 0);
    const expenseValues = labels.map((label) => expenseMap.get(label) || 0);
    const maxValue = Math.max(...incomeValues, ...expenseValues, 1);

    const bars = labels.map((label, index) => {
        const groupWidth = 560 / labels.length;
        const baseX = index * groupWidth + 26;
        const incomeHeight = (incomeValues[index] / maxValue) * 150;
        const expenseHeight = (expenseValues[index] / maxValue) * 150;
        return `
            <g>
                <rect x="${baseX}" y="${190 - incomeHeight}" width="18" height="${incomeHeight}" rx="6" fill="#177245"></rect>
                <rect x="${baseX + 24}" y="${190 - expenseHeight}" width="18" height="${expenseHeight}" rx="6" fill="#db5f36"></rect>
                <text x="${baseX + 21}" y="214" text-anchor="middle" class="axis-label">${escapeHtml(label)}</text>
            </g>
        `;
    }).join("");

    elements.incomeExpenseChart.innerHTML = `
        <div class="bar-chart-wrap">
            <div class="chart-key">
                <span><i class="legend-swatch" style="background:#177245"></i> Income</span>
                <span><i class="legend-swatch" style="background:#db5f36"></i> Expense</span>
            </div>
            <svg viewBox="0 0 600 230" class="bar-svg" role="img" aria-label="Income versus expense by month">
                <line x1="18" y1="190" x2="580" y2="190" stroke="rgba(28,25,23,0.14)"></line>
                ${bars}
            </svg>
        </div>
    `;
}

function renderAccounts() {
    if (!state.accounts.length) {
        elements.accountsList.innerHTML = '<p class="empty-state">No accounts yet.</p>';
        return;
    }

    elements.accountsList.innerHTML = state.accounts.map((account) => `
        <article class="list-card">
            <div>
                <strong>${escapeHtml(account.name)}</strong>
                <p>${escapeHtml(account.type)}</p>
            </div>
            <span>${formatCurrency(account.balance)}</span>
        </article>
    `).join("");
}

function renderCategories() {
    if (!state.categories.length) {
        elements.categoriesList.innerHTML = '<p class="empty-state">No categories yet.</p>';
        return;
    }

    elements.categoriesList.innerHTML = state.categories.map((category) => `
        <span class="category-chip" data-type="${escapeHtml(category.type)}">
            ${escapeHtml(category.name)} <small>${escapeHtml(category.type)}</small>
        </span>
    `).join("");
}

function renderBudgets() {
    if (!state.budgets.length) {
        elements.budgetsList.innerHTML = '<p class="empty-state">No budgets yet.</p>';
        return;
    }

    const sortedBudgets = [...state.budgets].sort((left, right) => (
        new Date(right.start_date) - new Date(left.start_date)
    ));

    elements.budgetsList.innerHTML = sortedBudgets.map((budget) => `
        <article class="budget-card-item">
            <div class="budget-card-top">
                <div>
                    <h3>${escapeHtml(budget.name)}</h3>
                    <p>${escapeHtml(budget.period)} • ${formatShortDate(budget.start_date)} to ${formatShortDate(budget.end_date)}</p>
                </div>
                <span class="budget-status" data-status="${escapeHtml(budget.status)}">${escapeHtml(budget.status)}</span>
            </div>
            <div class="budget-metrics">
                <div><span>Planned</span><strong>${formatCurrency(budget.amount)}</strong></div>
                <div><span>Spent</span><strong>${formatCurrency(budget.spent_amount)}</strong></div>
                <div><span>Remaining</span><strong>${formatCurrency(budget.remaining_amount)}</strong></div>
                <div><span>Usage</span><strong>${Number(budget.usage_percentage || 0).toFixed(1)}%</strong></div>
            </div>
            <div class="budget-progress">
                <div class="budget-progress-bar">
                    <span style="width: ${Math.min(Number(budget.usage_percentage || 0), 100)}%"></span>
                </div>
            </div>
            <div class="budget-category-breakdown">
                ${(budget.categories || []).length
                    ? budget.categories.map((category) => `
                        <div class="budget-category-item">
                            <div>
                                <strong>${escapeHtml(findCategoryName(category.category_id))}</strong>
                                <p>${formatCurrency(category.spent_amount)} / ${formatCurrency(category.allocated_amount)}</p>
                            </div>
                            <span>${Number(category.usage_percentage || 0).toFixed(1)}%</span>
                        </div>
                    `).join("")
                    : '<p class="empty-state">No category allocations available.</p>'}
            </div>
        </article>
    `).join("");
}

function renderTransactions() {
    if (!state.transactions.length) {
        elements.transactionsTable.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">No transactions yet.</td>
            </tr>
        `;
        return;
    }

    const accountMap = new Map(state.accounts.map((account) => [account.id, account.name]));
    const categoryMap = new Map(state.categories.map((category) => [category.id, category.name]));

    const sortedTransactions = [...state.transactions].sort((left, right) => (
        new Date(right.transaction_date) - new Date(left.transaction_date)
    ));

    elements.transactionsTable.innerHTML = sortedTransactions.map((transaction) => `
        <tr>
            <td>${formatDate(transaction.transaction_date)}</td>
            <td>${escapeHtml(transaction.description || "No description")}</td>
            <td><span class="type-pill" data-type="${escapeHtml(transaction.type)}">${escapeHtml(transaction.type)}</span></td>
            <td>${formatCurrency(transaction.amount)}</td>
            <td>${escapeHtml(accountMap.get(transaction.account_id) || `#${transaction.account_id}`)}</td>
            <td>${escapeHtml(categoryMap.get(transaction.category_id) || `#${transaction.category_id}`)}</td>
        </tr>
    `).join("");
}

function fillTransactionSelects() {
    elements.transAccount.innerHTML = createSelectOptions(
        state.accounts,
        "Choose account",
        (account) => ({
            value: account.id,
            label: `${account.name} (${formatCurrency(account.balance)})`,
        }),
    );

    elements.transCategory.innerHTML = createSelectOptions(
        state.categories,
        "Choose category",
        (category) => ({
            value: category.id,
            label: `${category.name} [${category.type}]`,
        }),
    );
}

function syncTransactionTypeFromCategory() {
    const selectedCategoryId = Number(elements.transCategory.value);
    const category = state.categories.find((item) => item.id === selectedCategoryId);

    if (!category) {
        elements.transTypeDisplay.value = "Select a category first";
        return;
    }

    elements.transTypeDisplay.value = category.type === "income" ? "Income" : "Expense";
}

function syncBudgetCategoryRows() {
    const availableBudgetCategories = state.categories.filter((category) => category.type === "expense");

    elements.budgetCategoryHint.textContent = availableBudgetCategories.length
        ? "Choose from your available expense categories in the dropdown below."
        : "No expense categories available yet. Create one first, then assign it to a budget.";
    elements.addBudgetCategoryBtn.disabled = !availableBudgetCategories.length;

    const rows = elements.budgetCategoryRows.querySelectorAll(".allocation-row");
    if (!rows.length) {
        addBudgetCategoryRow();
        return;
    }

    rows.forEach((row) => {
        const select = row.querySelector('[name="budget_category_id"]');
        const selectedValue = select.value;
        select.innerHTML = createSelectOptions(
            availableBudgetCategories,
            "Choose expense category",
            (category) => ({
                value: category.id,
                label: category.name,
            }),
        );
        select.disabled = !availableBudgetCategories.length;
        if (selectedValue) {
            select.value = selectedValue;
        }
    });
}

function addBudgetCategoryRow() {
    const row = document.createElement("div");
    row.className = "allocation-row";
    row.innerHTML = `
        <label class="allocation-field">
            <span>Category</span>
            <select name="budget_category_id" required></select>
        </label>
        <input name="allocated_amount" type="number" min="0" step="0.01" placeholder="Allocated amount" required>
        <input name="alert_percentage" type="number" min="1" max="100" value="80" placeholder="Alert %" required>
        <button class="ghost-button small-button" type="button" data-action="remove-budget-row">Remove</button>
    `;
    elements.budgetCategoryRows.appendChild(row);
    syncBudgetCategoryRows();
}

function handleBudgetCategoryRowActions(event) {
    const button = event.target.closest("button[data-action='remove-budget-row']");
    if (!button) {
        return;
    }

    const rows = elements.budgetCategoryRows.querySelectorAll(".allocation-row");
    if (rows.length === 1) {
        logActivity("Budget row kept", "At least one budget category row is required.");
        return;
    }

    button.closest(".allocation-row").remove();
}

function createSelectOptions(items, placeholder, mapper) {
    const placeholderOption = `<option value="" ${items.length ? "" : "selected"} disabled>${placeholder}</option>`;
    const options = items.map((item) => {
        const mapped = mapper(item);
        return `<option value="${mapped.value}">${escapeHtml(mapped.label)}</option>`;
    }).join("");
    return placeholderOption + options;
}

function aggregateExpenseByCategory() {
    const expenseTransactions = state.transactions.filter((transaction) => transaction.type === "expense");
    const totals = new Map();

    expenseTransactions.forEach((transaction) => {
        const label = findCategoryName(transaction.category_id);
        totals.set(label, (totals.get(label) || 0) + Number(transaction.amount));
    });

    return totals;
}

function aggregateMonthlyTotals(type) {
    const totals = new Map();
    const filtered = state.transactions
        .filter((transaction) => transaction.type === type)
        .sort((left, right) => new Date(left.transaction_date) - new Date(right.transaction_date));

    filtered.forEach((transaction) => {
        const label = new Date(transaction.transaction_date).toLocaleDateString("en-IN", {
            month: "short",
            year: "2-digit",
        });
        totals.set(label, (totals.get(label) || 0) + Number(transaction.amount));
    });

    return totals;
}

function buildLinePoints(values, width, height) {
    const maxValue = Math.max(...values, 1);
    const stepX = values.length > 1 ? (width - 40) / (values.length - 1) : 0;

    return values.map((value, index) => {
        const x = 20 + index * stepX;
        const y = 20 + (1 - value / maxValue) * (height - 60);
        return { x, y };
    });
}

function renderSvgChart({ width, height, lines, labels, values, title }) {
    const maxValue = Math.max(...values, 1);
    const lineMarkup = lines.map((line) => {
        const path = line.points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
        const areaPath = `${path} L ${line.points[line.points.length - 1].x} ${height - 30} L ${line.points[0].x} ${height - 30} Z`;
        const dots = line.points.map((point) => `
            <circle cx="${point.x}" cy="${point.y}" r="4" fill="${line.color}"></circle>
        `).join("");

        return `
            ${line.area ? `<path d="${areaPath}" fill="${line.color}" opacity="0.12"></path>` : ""}
            <path d="${path}" fill="none" stroke="${line.color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
            ${dots}
        `;
    }).join("");

    const axisLabels = labels.map((label, index) => `
        <text x="${lines[0].points[index].x}" y="${height - 8}" text-anchor="middle" class="axis-label">${escapeHtml(label)}</text>
    `).join("");

    return `
        <svg viewBox="0 0 ${width} ${height}" class="line-svg" role="img" aria-label="${escapeHtml(title)}">
            <line x1="20" y1="${height - 30}" x2="${width - 20}" y2="${height - 30}" stroke="rgba(28,25,23,0.14)"></line>
            <line x1="20" y1="20" x2="20" y2="${height - 30}" stroke="rgba(28,25,23,0.1)"></line>
            <text x="22" y="18" class="axis-value">${escapeHtml(compactCurrency(maxValue))}</text>
            ${lineMarkup}
            ${axisLabels}
        </svg>
    `;
}

function describeArc(cx, cy, radius, startAngle, endAngle) {
    const start = polarToCartesian(cx, cy, radius, endAngle);
    const end = polarToCartesian(cx, cy, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= Math.PI ? "0" : "1";

    return [
        `M ${cx} ${cy}`,
        `L ${start.x} ${start.y}`,
        `A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`,
        "Z",
    ].join(" ");
}

function polarToCartesian(cx, cy, radius, angleInRadians) {
    return {
        x: cx + radius * Math.cos(angleInRadians),
        y: cy + radius * Math.sin(angleInRadians),
    };
}

function chartColor(index) {
    const palette = ["#db5f36", "#177245", "#d9a441", "#34699a", "#8a5a9d", "#d9776a", "#5aa68d"];
    return palette[index % palette.length];
}

function updateSessionUI() {
    elements.tokenPreview.textContent = state.token
        ? `${state.token.slice(0, 24)}...`
        : "No active token";
}

function requireAuth() {
    if (state.token) {
        return true;
    }

    logActivity("Authentication required", "Please log in first.");
    return false;
}

function logout() {
    state.token = "";
    localStorage.removeItem("finance_token");
    updateSessionUI();
    elements.budgetForm.reset();
    renderEmptyState();
    logActivity("Logged out", "Local session cleared.");
}

function logActivity(title, payload) {
    const timestamp = new Date().toLocaleTimeString();
    const content = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
    elements.activityLog.textContent = `[${timestamp}] ${title}\n${content}`;
}

function formatCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(Number(value || 0));
}

function formatDate(value) {
    return new Date(value).toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

function formatShortDate(value) {
    return new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}

function compactCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        notation: "compact",
        maximumFractionDigits: 1,
    }).format(Number(value || 0));
}

function findCategoryName(categoryId) {
    const match = state.categories.find((category) => category.id === categoryId);
    return match ? match.name : `Category #${categoryId}`;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
