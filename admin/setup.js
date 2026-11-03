(async function () {
  'use strict';
  var status = document.getElementById('cms-status');
  try {
    var response = await fetch('config.yml', { cache: 'no-store' });
    if (!response.ok) throw new Error('无法读取后台配置');
    // config.yml intentionally uses JSON, which is valid YAML as well.
    var config = await response.json();
    var local = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
    if (!local && !config.backend.base_url) {
      status.textContent = '线上 GitHub 登录尚未配置：请在 admin/config.yml 的 backend 中设置 OAuth 服务的 base_url 和 auth_endpoint。当前可使用本地后台，具体步骤见仓库 README。';
      return;
    }
    if (!window.CMS) throw new Error('Decap CMS 加载失败，请检查网络后重试');
    window.CMS.init({ config: Object.assign({}, config, { load_config_file: false }) });
    status.remove();
  } catch (error) {
    status.textContent = error.message;
  }
}());
