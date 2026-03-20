// Auto-detects environment — no manual switching needed ever again
const CONFIG = {
  API: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:5000/api'
    : 'https://vmt-backend-4tpn.onrender.com/api'
};