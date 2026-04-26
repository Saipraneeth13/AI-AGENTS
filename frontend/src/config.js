export const API_URL = import.meta.env.VITE_API_URL || '';
export const WS_URL = API_URL 
  ? API_URL.replace(/^http/, 'ws') 
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;
