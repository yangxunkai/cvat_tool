const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new (require('webpack')).DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
      }),
    ],
  },
  devServer: {
    hot: false,         // 禁用热更新
    liveReload: false,  // 禁用实时重新加载
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws', // 设置为自动以避免错误的连接地址
    },
  },
});
module.exports = {
	publicPath: "./",
}
