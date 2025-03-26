// vite.config.js
export default {
  server: {
    host: '0.0.0.0',  // 让 Vite 服务器监听所有 IP 地址
    port: 3000,       // React 默认运行在 3000 端口
  },
  define: {
    'process.env': {},
  },
  // 设置代理，将所有 `/api` 请求转发到 Django 的 8000 端口
  proxy: {
    '/api': {
      target: 'http://51.21.191.188:8000',  // Django 后端地址
      changeOrigin: true,  // 允许跨域请求
      secure: false,  // 禁用 SSL 校验
    },
  },
};
