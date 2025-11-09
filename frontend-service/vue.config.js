const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_URL || 'http://api-gateway:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  },
  configureWebpack: {
    performance: {
      hints: false
    }
  },
  css: {
    loaderOptions: {
      css: {
        modules: {
          auto: () => true
        }
      }
    }
  }
})
