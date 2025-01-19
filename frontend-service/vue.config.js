module.exports = {
    devServer: {
        proxy: {
            '/api': {
                target: 'http://api-gateway:5000',
                changeOrigin: true,
                pathRewrite: {
                    '^/api': ''
                }
            }
        }
    }
};