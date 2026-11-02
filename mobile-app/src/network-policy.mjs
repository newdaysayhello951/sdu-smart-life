export function normalizeServer(value, allowLanHttp = false) {
  const url = new URL(value.trim());
  if (url.username || url.password || url.search || url.hash || url.pathname !== '/') throw new Error('请填写服务根地址，不包含路径、账号或查询参数');
  const lan = /^(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)$/.test(url.hostname) || /^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$/.test(url.hostname);
  if (url.protocol !== 'https:' && !(allowLanHttp && lan && url.protocol === 'http:')) throw new Error('正式服务需要 HTTPS；开发版仅允许局域网 HTTP');
  return url.origin;
}
export function isApiPath(path) { return typeof path === 'string' && /^\/api\//.test(path) && !/[\\\r\n]/.test(path); }
export function parseSse(block) {
  let event = 'message'; const data = [];
  for (const line of block.replace(/\r\n/g, '\n').split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''));
  }
  return data.length ? {event, data:data.join('\n')} : null;
}
