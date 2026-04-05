let allTodos = [];
let currentFilter = 'all';
let currentSort   = 'default';

const PRIORITY_RANK = { high: 0, medium: 1, low: 2 };

function sortedTodos(list) {
    const arr = [...list];
    if (currentSort === 'priority') {
        arr.sort((a, b) => {
            const pd = PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority];
            return pd !== 0 ? pd : a.id - b.id;
        });
    } else if (currentSort === 'date') {
        arr.sort((a, b) => {
            if (!a.due_date && !b.due_date) return a.id - b.id;
            if (!a.due_date) return 1;
            if (!b.due_date) return -1;
            return a.due_date < b.due_date ? -1 : a.due_date > b.due_date ? 1 : a.id - b.id;
        });
    } else {
        arr.sort((a, b) => a.id - b.id);
    }
    return arr;
}

function setSort(sort, el) {
    currentSort = sort;
    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    renderTodos();
}

// ── 인증 ────────────────────────────────────────────────────
const getToken   = () => localStorage.getItem('token');
const setToken   = t  => localStorage.setItem('token', t);
const clearToken = () => localStorage.removeItem('token');

const authHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
});

async function apiFetch(url, opts = {}) {
    const res = await fetch(url, { ...opts, headers: authHeaders() });
    if (res.status === 401) { logout(); return null; }
    return res;
}

// ── 화면 전환 ────────────────────────────────────────────────
function showMain() {
    document.getElementById('auth-section').classList.remove('visible');
    document.getElementById('main-section').classList.add('visible');
    fetchTodos();
}

function showAuth() {
    document.getElementById('auth-section').classList.add('visible');
    document.getElementById('main-section').classList.remove('visible');
}

function showTab(tab) {
    document.getElementById('login-form').style.display    = tab === 'login'    ? '' : 'none';
    document.getElementById('register-form').style.display = tab === 'register' ? '' : 'none';
    document.querySelectorAll('.auth-tab-btn').forEach((b, i) => {
        b.classList.toggle('active', (tab === 'login' && i === 0) || (tab === 'register' && i === 1));
    });
    document.getElementById('auth-error').style.display = 'none';
}

function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg;
    el.style.display = 'block';
}

function logout() { clearToken(); allTodos = []; showAuth(); }

// ── 로그인 / 회원가입 ────────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async e => {
    e.preventDefault();
    const res = await fetch('/auth/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email:    document.getElementById('login-email').value,
            password: document.getElementById('login-password').value
        })
    });
    if (res.ok) { setToken((await res.json()).access_token); showMain(); }
    else showAuthError((await res.json()).detail || '로그인에 실패했습니다.');
});

document.getElementById('register-form').addEventListener('submit', async e => {
    e.preventDefault();
    const email    = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const res = await fetch('/auth/register', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (res.ok) {
        const lr = await fetch('/auth/login', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (lr.ok) { setToken((await lr.json()).access_token); showMain(); }
    } else {
        showAuthError((await res.json()).detail || '회원가입에 실패했습니다.');
    }
});

// ── 기한 상태 ────────────────────────────────────────────────
function getDueStatus(due_date, completed) {
    if (completed || !due_date) return 'none';
    const today = new Date().toISOString().split('T')[0];
    if (due_date < today)   return 'overdue';
    if (due_date === today) return 'today';
    return 'upcoming';
}

function dueBadgeHtml(due_date, status) {
    if (!due_date) return '';
    if (status === 'overdue') {
        const days = Math.round(
            (new Date(new Date().toISOString().split('T')[0]) - new Date(due_date)) / 86400000
        );
        return `<span class="badge badge-overdue">${days}일 초과</span>`;
    }
    if (status === 'today') return `<span class="badge badge-today">오늘 마감</span>`;
    return `<span class="badge badge-upcoming">${due_date}</span>`;
}

// ── Todo 목록 ────────────────────────────────────────────────
async function fetchTodos() {
    const res = await apiFetch('/todos');
    if (!res) return;
    allTodos = await res.json();
    renderTodos();
}

function renderTodos() {
    const list  = document.getElementById('todo-list');
    const stats = document.getElementById('stats');
    list.innerHTML = '';

    const filtered = sortedTodos(allTodos.filter(t => {
        if (currentFilter === 'active')    return !t.completed;
        if (currentFilter === 'completed') return  t.completed;
        return true;
    }));

    const done = allTodos.filter(t => t.completed).length;
    stats.textContent = `${done} / ${allTodos.length} 완료`;

    if (filtered.length === 0) {
        list.innerHTML = '<div class="empty-state">할 일이 없습니다</div>';
        return;
    }

    const buckets = { overdue: [], today: [], upcoming: [], none: [] };
    filtered.forEach(t => buckets[getDueStatus(t.due_date, t.completed)].push(t));

    const sections = [
        { key: 'overdue',  label: '기한 초과', cls: 'section-overdue'  },
        { key: 'today',    label: '오늘 마감', cls: 'section-today'    },
        { key: 'upcoming', label: '예정',       cls: 'section-upcoming' },
        { key: 'none',     label: '날짜 없음', cls: 'section-none'     },
    ];

    const active = sections.filter(s => buckets[s.key].length > 0);
    const showHeader = active.length > 1;

    active.forEach(({ key, label, cls }) => {
        if (showHeader) {
            const hdr = document.createElement('div');
            hdr.innerHTML = `<span class="section-header ${cls}">${label}</span>`;
            list.appendChild(hdr);
        }
        buckets[key].forEach(t => list.appendChild(makeTodoCard(t)));
    });
}

function makeTodoCard(todo) {
    const status = getDueStatus(todo.due_date, todo.completed);
    const priorityBadge = {
        high:   '<span class="badge badge-high">높음</span>',
        medium: '<span class="badge badge-medium">보통</span>',
        low:    '<span class="badge badge-low">낮음</span>'
    }[todo.priority] || '';

    let cardCls = todo.completed ? 'done' : (status !== 'none' ? status : '');

    const el = document.createElement('div');
    el.className = `todo-card ${cardCls}`;
    el.innerHTML = `
        <input type="checkbox" class="todo-check" ${todo.completed ? 'checked' : ''}
               onchange="toggleTodo(${todo.id})">
        <div class="todo-body">
            <div class="todo-title ${todo.completed ? 'done-text' : ''}">
                ${todo.title}
                ${priorityBadge}
                ${dueBadgeHtml(todo.due_date, status)}
            </div>
            ${todo.description ? `<div class="todo-desc">${todo.description}</div>` : ''}
        </div>
        <div class="todo-actions">
            <button class="btn-icon" onclick="openEdit(${todo.id})" title="수정">✎</button>
            <button class="btn-icon del" onclick="deleteTodo(${todo.id})" title="삭제">✕</button>
        </div>`;
    return el;
}

function filterTodos(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderTodos();
}

async function toggleTodo(id) {
    const res = await apiFetch(`/todos/${id}/toggle`, { method: 'PATCH' });
    if (res?.ok) fetchTodos();
}

async function deleteTodo(id) {
    if (!confirm('삭제하시겠습니까?')) return;
    const res = await apiFetch(`/todos/${id}`, { method: 'DELETE' });
    if (res?.ok) fetchTodos();
}

// ── 수정 모달 ────────────────────────────────────────────────
function openEdit(id) {
    const t = allTodos.find(t => t.id === id);
    document.getElementById('edit-id').value          = t.id;
    document.getElementById('edit-title').value       = t.title;
    document.getElementById('edit-description').value = t.description || '';
    document.getElementById('edit-priority').value    = t.priority;
    document.getElementById('edit-due_date').value    = t.due_date || '';
    document.getElementById('editOverlay').classList.add('open');
}

function closeModal() {
    document.getElementById('editOverlay').classList.remove('open');
}

document.getElementById('editOverlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
});

async function submitEdit() {
    const id       = document.getElementById('edit-id').value;
    const due_date = document.getElementById('edit-due_date').value;
    const res = await apiFetch(`/todos/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            title:       document.getElementById('edit-title').value,
            description: document.getElementById('edit-description').value,
            priority:    document.getElementById('edit-priority').value,
            due_date:    due_date || null
        })
    });
    if (res?.ok) { closeModal(); fetchTodos(); }
}

document.getElementById('todo-form').addEventListener('submit', async e => {
    e.preventDefault();
    const due_date = document.getElementById('due_date').value;
    const res = await apiFetch('/todos', {
        method: 'POST',
        body: JSON.stringify({
            title:       document.getElementById('title').value,
            priority:    document.getElementById('priority').value,
            description: document.getElementById('description').value,
            due_date:    due_date || null
        })
    });
    if (res?.ok) { e.target.reset(); fetchTodos(); }
});

// ── 진입 ─────────────────────────────────────────────────────
if (getToken()) showMain(); else showAuth();
