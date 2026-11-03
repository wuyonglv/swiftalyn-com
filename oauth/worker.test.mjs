import test from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import worker from './worker.mjs';
globalThis.crypto ??= webcrypto;
const env = { GITHUB_OAUTH_ID: 'test-id', GITHUB_OAUTH_SECRET: 'test-secret', ALLOWED_ORIGINS: 'https://swiftalyn.com' };
const request = path => new Request(`https://auth.example${path}`);

test('login requires configured credentials and an allowed CMS origin', async () => {
  assert.equal((await worker.fetch(request('/auth?provider=github&site_id=swiftalyn.com'), {})).status, 503);
  assert.equal((await worker.fetch(request('/auth?provider=github&site_id=evil.example'), env)).status, 403);
  assert.equal((await worker.fetch(request('/auth?provider=gitlab&site_id=swiftalyn.com'), env)).status, 400);
});

test('login issues a secure state cookie and correct GitHub redirect', async () => {
  const response = await worker.fetch(request('/auth?provider=github&site_id=swiftalyn.com'), env);
  assert.equal(response.status, 302);
  const location = new URL(response.headers.get('location'));
  assert.equal(location.origin, 'https://github.com');
  assert.equal(location.searchParams.get('redirect_uri'), 'https://auth.example/callback');
  assert.equal(location.searchParams.get('scope'), 'public_repo');
  assert.match(location.searchParams.get('state'), /^[a-f0-9]{64}$/);
  assert.match(response.headers.get('set-cookie'), /Secure; HttpOnly; SameSite=Lax/);
});

test('callback rejects missing or mismatched state before requesting a token', async () => {
  assert.equal((await worker.fetch(request('/callback?code=fake&state=wrong'), env)).status, 400);
  const response = await worker.fetch(request('/auth?provider=github&site_id=swiftalyn.com'), env);
  const callback = new Request('https://auth.example/callback?code=fake&state=wrong', {
    headers: { Cookie: response.headers.get('set-cookie').split(';')[0] }
  });
  assert.equal((await worker.fetch(callback, env)).status, 403);
});

test('valid callback exchanges code and sends token only to the permitted opener', async () => {
  const response = await worker.fetch(request('/auth?provider=github&site_id=swiftalyn.com'), env);
  const nonce = new URL(response.headers.get('location')).searchParams.get('state');
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'https://github.com/login/oauth/access_token');
    assert.equal(JSON.parse(options.body).client_secret, 'test-secret');
    return Response.json({ access_token: 'test-token' });
  };
  try {
    const callback = new Request(`https://auth.example/callback?code=test-code&state=${nonce}`, {
      headers: { Cookie: response.headers.get('set-cookie').split(';')[0] }
    });
    const result = await worker.fetch(callback, env);
    const page = await result.text();
    assert.equal(result.status, 200);
    assert.match(page, /authorization:github:success/);
    assert.match(page, /event\.origin !== origin/);
    assert.match(page, /event\.source !== window\.opener/);
    assert.ok(!page.includes('test-secret'));
    assert.match(result.headers.get('set-cookie'), /Max-Age=0/);
  } finally { globalThis.fetch = originalFetch; }
});
