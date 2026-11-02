# swiftalyn-com
## Featured Products（本地商品）

首页商品由 `data/products.js` 中的 `window.SWIFTALYN_PRODUCTS` 管理，
由 `js/products.js` 展示，不再初始化 GoDaddy 商品组件或调用商品接口。
直接打开 HTML 或通过静态服务器访问均可，无需构建。

原商品接口在迁移时返回 HTTP 504。目前已根据提供的原商品 HTML 录入全部四个商品的
原始 ID、完整名称和价格（£24.99、£12.99、£19.99、£19.99）。已按提供的 CSS 图片对应关系，
将全部四张商品图片下载到 `images/products/`，页面仅引用本地图片。
商品详情链接尚待补充。
数组为空时，页面显示“New products are coming soon!”。

将核实的商品加入数组，例如（仅为格式说明，不代表真实商品）：

```js
window.SWIFTALYN_PRODUCTS = [
  {
    id: 'product-id',
    name: '实际商品名称',
    price: 19.99,
    currency: 'GBP',
    image: 'images/products/product.jpg',
    imageAlt: '商品图片说明',
    description: '实际商品描述',
    href: 'product.html'
  }
];
```

图片应保存到仓库，链接填写已存在的本站页面；没有详情页可省略 `href`。
价格和币种同时提供时才显示价格。此修改仅替换商品区域的数据和展示，
网站其余 GoDaddy 布局、联系表单等组件仍保留原有实现。

## 首页样式

首页原有的 15 段内嵌 CSS 和商品模块样式统一维护在 `css/styles.css`。
字体通过 `../fonts/` 引用，媒体查询顺序保持不变。
GoDaddy 组件运行时仍可能生成动态样式；隐私政策和条款页保留各自的内嵌样式。
