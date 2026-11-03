const COOKIE = '__Host-decap-state';
const cookie = (value, age = 600) => `${COOKIE}=${value}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=${age}`;
const headers = { 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer' };
const fail = (message, status = 400) => new Response(message, { status, headers });
const js = value => JSON.stringify(value).replace(/</g, '\\u003c');

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/') return new Response('Swiftalyn CMS OAuth is running.', { headers });
    if (!['/auth', '/callback'].includes(url.pathname)) return fail('Not found', 404);
    if (request.method !== 'GET') return fail('Method not allowed', 405);
    if (!env.GITHUB_OAUTH_ID || !env.GITHUB_OAUTH_SECRET) return fail('GitHub OAuth credentials have not been configured.', 503);
    const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
    if (url.pathname === '/auth') {
      if (url.searchParams.get('provider') !== 'github') return fail('Unsupported provider');
      let origin;
      try {
        const site = url.searchParams.get('site_id');
        if (!site) return fail('Missing site_id');
        origin = new URL(site.includes('://') ? site : `https://${site}`).origin;
      } catch { return fail('Invalid site_id'); }
      if (!allowed.includes(origin)) return fail('CMS origin is not allowed', 403);
      const bytes = crypto.getRandomValues(new Uint8Array(32));
      const nonce = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
      const state = btoa(JSON.stringify({ nonce, origin }));
      const github = new URL('https://github.com/login/oauth/authorize');
      github.search = new URLSearchParams({
        client_id: env.GITHUB_OAUTH_ID,
        redirect_uri: `${url.origin}/callback`,
        scope: env.GITHUB_REPO_PRIVATE === '1' ? 'repo' : 'public_repo',
        state: nonce
      }).toString();
      return new Response(null, { status: 302, headers: { ...headers, Location: github.href, 'Set-Cookie': cookie(state) } });
    }
    const saved = (request.headers.get('Cookie') || '').split(';').map(s => s.trim()).find(s => s.startsWith(`${COOKIE}=`));
    let state;
    try { state = JSON.parse(atob(saved.slice(COOKIE.length + 1))); }
    catch { return fail('Login expired. Close this window and try again.'); }
    if (!state.nonce || state.nonce !== url.searchParams.get('state') || !allowed.includes(state.origin)) return fail('Invalid OAuth state', 403);
    const code = url.searchParams.get('code');
    if (!code) return fail('GitHub authorization was declined or no code was returned.');
    let data;
    try {
      const response = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: env.GITHUB_OAUTH_ID, client_secret: env.GITHUB_OAUTH_SECRET, code, redirect_uri: `${url.origin}/callback` })
      });
      if (!response.ok) return fail('GitHub token exchange failed. Please retry.', 502);
      data = await response.json();
    } catch { return fail('Could not contact GitHub. Please retry.', 502); }
    if (!data.access_token) return fail('GitHub did not issue a token. Check the OAuth application configuration.', 502);
    const message = `authorization:github:success:${JSON.stringify({ token: data.access_token, provider: 'github' })}`;
    const page = `<!doctype html><meta charset="utf-8"><title>Swiftalyn CMS Login</title><p>Completing sign in…</p><script>
const origin=${js(state.origin)}, payload=${js(message)};
if(window.opener){
  const receive = event => {
    if(event.source !== window.opener || event.origin !== origin || event.data !== 'authorizing:github') return;
    window.removeEventListener('message',receive);
    window.opener.postMessage(payload,origin);
  };
  window.addEventListener('message',receive);
  window.opener.postMessage('authorizing:github',origin);
}else{document.querySelector('p').textContent='Open login from the CMS admin page.';}
</script>`;
    return new Response(page, { headers: { ...headers, 'Content-Type': 'text/html; charset=utf-8', 'Set-Cookie': cookie('', 0), 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; frame-ancestors 'none'" } });
  }
};
