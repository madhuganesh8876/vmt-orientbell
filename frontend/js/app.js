const API = 'https://vmt-backend-4tpn.onrender.com/api';

// Show toast notification
function showToast(message, type = 'success') {
  let toast = document.getElementById('vmt-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'vmt-toast';
    toast.className = 'vmt-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = `vmt-toast ${type} show`;
  setTimeout(() => toast.classList.remove('show'), 3500);
}

// API helper
async function apiCall(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('vmt_token');
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  };
  if (body) options.body = JSON.stringify(body);

  try {
    const res = await fetch(`${API}${endpoint}`, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Something went wrong');
    return data;
  } catch (err) {
    showToast(err.message, 'error');
    throw err;
  }
}

// Save user to localStorage
function saveUser(token, user) {
  localStorage.setItem('vmt_token', token);
  localStorage.setItem('vmt_user', JSON.stringify(user));
}

// Get current user
function getUser() {
  const user = localStorage.getItem('vmt_user');
  return user ? JSON.parse(user) : null;
}

// Logout
function logout() {
  localStorage.removeItem('vmt_token');
  localStorage.removeItem('vmt_user');
  window.location.href = 'index.html';
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

// Protect page - redirect if not logged in
function requireAuth(allowedRoles = []) {
  const user = getUser();
  if (!user) {
    window.location.href = 'index.html';
    return null;
  }
  if (allowedRoles.length && !allowedRoles.includes(user.role)) {
    showToast('Access denied', 'error');
    setTimeout(() => window.location.href = 'index.html', 1500);
    return null;
  }
  return user;
}