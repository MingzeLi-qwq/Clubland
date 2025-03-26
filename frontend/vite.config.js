export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://51.21.191.188:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
};
