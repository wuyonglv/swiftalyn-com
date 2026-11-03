# swiftalyn-com

## 内容管理（Decap CMS）

后台入口：站点的 `admin/`。已开放：

- 首页横幅文字（支持换行）
- About 标题及三个内容块
- 供应商 / 经销商的标题与正文
- Featured Products 标题、空列表提示，以及商品的新增、删除、排序、名称、价格、币种、图片、描述和本站详情链接
- 页脚版权文字

内容源为 `content/home.json` 和 `content/products.json`。图片保存在 `images/`，
后台上传图片保存在 `images/uploads/`。地图和联系表单继续使用原有组件，本次未开放这些组件的编辑。
About 固定三个内容块，合作伙伴固定两个，以匹配现有布局。

## 本地编辑和预览

需要 Python 3 和 Node.js。先在仓库根目录运行：

```sh
python3 scripts/serve.py
```

另开终端，在同一个仓库根目录运行：

```sh
npx decap-server
```

打开 `http://localhost:8000/admin/`。本地后台将修改写入仓库的 `content/` 和 `images/`。
保存后刷新 `http://localhost:8000/` 即可查看结果，预览服务会在每次访问首页时自动重新构建，
并禁用浏览器缓存。若仍在运行旧的 `python3 -m http.server`，请先按 Ctrl+C 停止，
再运行 `python3 scripts/serve.py`。构建失败会在页面返回错误，详细原因显示在预览终端。
请仅在本机运行本地代理。

`index.html` 是布局模板，`data/products.js` 是构建时在 `_site/` 中生成的文件。
后续请修改 JSON 内容源；不要直接打开模板作为内容预览，也不要修改生成目录。
构建只使用 Python 标准库，无需安装 Python 依赖。其他静态托管平台同样使用
`python3 scripts/build.py` 构建并发布 `_site/`。

## GitHub Pages 发布

仓库提供 `.github/workflows/pages.yml`。在 GitHub 仓库 Settings → Pages 中将
Source 设为 **GitHub Actions**。推送到 `main` 后自动构建并部署 `_site/`。
后台发布内容会提交到 `wuyonglv/swiftalyn-com` 的 `main` 分支，随后触发相同构建。
如果使用自定义域名，请在仓库根目录保留相应 `CNAME` 文件，构建会复制它。

## 线上登录：尚待接入 OAuth

目前没有提供 OAuth 服务，所以线上后台会显示配置提示，不会显示不可用的登录按钮。
GitHub Pages 只托管静态文件；Decap GitHub 后端需要额外的 OAuth 认证服务，且编辑者需具有仓库写权限。

取得兼容 Decap 的认证服务地址后，在 `admin/config.yml` 的 `backend` 对象中补充：

```json
"base_url": "https://你的认证服务域名",
"auth_endpoint": "auth"
```

该文件采用 JSON 语法（也是合法 YAML），修改时注意逗号。
OAuth 回调地址由认证服务决定，需按服务说明在 GitHub OAuth App 中登记。
Client Secret 只配置在认证服务端，不得写入仓库或静态页面。
当前未创建 OAuth App、未部署认证服务、未更改 GitHub Pages 设置。
参考：https://decapcms.org/docs/github-backend/

## 样式

首页样式统一维护在 `css/styles.css`，字体通过 `../fonts/` 引用。
原有组件运行时仍可能生成动态样式；隐私政策和条款页保留各自的内嵌样式。
