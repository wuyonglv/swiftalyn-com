# swiftalyn-com

## 内容管理（Decap CMS）

后台入口：站点的 `admin/`。已开放：

- 首页横幅文字（支持换行）
- About 标题及三个内容块
- 供应商 / 经销商的标题与正文
- Featured Products 标题、空列表提示，以及商品的新增、删除、排序、名称、价格、币种、图片、描述和本站详情链接
- Contact Us 标题、公司名称、地址、电话、展示邮箱、营业时间、地图位置、表单标题、收件邮箱和邮件主题
- 页脚版权文字

内容源为 `content/home.json`、`content/products.json` 和 `content/contact.json`。图片保存在 `images/`，
后台上传图片保存在 `images/uploads/`。地图和联系表单继续使用原有组件，构建会同步更新其初始化配置。
Contact Us 在后台中是独立的“Contact Us 联系我们”入口。星期需各出现一次，时间采用 24 小时制。
更换表单收件邮箱后需在新邮箱完成 FormSubmit 的激活验证；更换地图地址时还需同步调整坐标。
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

## 线上登录（Cloudflare OAuth）

认证 Worker 已部署到 `https://swiftalyn-cms-auth.swiftalyn-cms.workers.dev`，
源码为 `oauth/worker.mjs`，配置为 `oauth/wrangler.toml`。网站后台配置已指向该地址。
已确认 Worker 中存在两项 OAuth 凭据，且 `/auth` 可正常跳转至 GitHub。
完整登录授权仍需在浏览器中验证。以下步骤供后续维护或重新配置使用。

在 https://github.com/settings/applications/new 创建 OAuth App：

- Application name：`Swiftalyn CMS`
- Homepage URL：`https://swiftalyn-cms-auth.swiftalyn-cms.workers.dev`
- Authorization callback URL：`https://swiftalyn-cms-auth.swiftalyn-cms.workers.dev/callback`

创建后生成 Client Secret。在本项目根目录分别执行以下命令，按提示输入对应值：

```sh
npm exec --yes --package=wrangler@4.59.1 -- wrangler secret put GITHUB_OAUTH_ID --config oauth/wrangler.toml
npm exec --yes --package=wrangler@4.59.1 -- wrangler secret put GITHUB_OAUTH_SECRET --config oauth/wrangler.toml
```

凭据只保存到 Cloudflare，不写入仓库或聊天记录。`GITHUB_OAUTH_ID` 对应 Client ID，
`GITHUB_OAUTH_SECRET` 对应 Client Secret。两项保存后不需要重新部署 Worker。
编辑者必须对 `wuyonglv/swiftalyn-com` 有写入权限。

Worker 允许的后台来源在 `oauth/wrangler.toml` 的 `ALLOWED_ORIGINS` 中配置。
若后台域名改变，需同步修改并重新部署 Worker。私有仓库需要将
`GITHUB_REPO_PRIVATE` 改为 `"1"` 后重新部署并重新授权。

```sh
node --test oauth/worker.test.mjs
npm exec --yes --package=wrangler@4.59.1 -- wrangler deploy --config oauth/wrangler.toml
```

本地后台仍使用 `decap-server`，不依赖线上 OAuth。

## 样式

首页样式统一维护在 `css/styles.css`，字体通过 `../fonts/` 引用。
原有组件运行时仍可能生成动态样式；隐私政策和条款页保留各自的内嵌样式。
