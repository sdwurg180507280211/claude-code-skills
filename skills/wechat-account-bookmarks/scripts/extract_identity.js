#!/usr/bin/env node
const path = require('path');

async function main() {
  const [extractorPath, url] = process.argv.slice(2);
  if (!extractorPath || !url) {
    console.error('usage: node extract_identity.js <upstream-extract.js> <wechat-article-url>');
    process.exit(2);
  }

  const mod = require(path.resolve(extractorPath));
  if (!mod || typeof mod.extract !== 'function') {
    throw new Error(`upstream extractor does not export extract(): ${extractorPath}`);
  }

  const result = await mod.extract(url, {
    shouldReturnContent: false,
    shouldReturnRawMeta: false,
    shouldFollowTransferLink: true,
    shouldExtractMpLinks: false,
    shouldExtractTags: false,
    shouldExtractRepostMeta: false
  });

  if (!result || result.done !== true) {
    console.log(JSON.stringify({
      ok: false,
      code: result?.code ?? null,
      message: result?.msg ?? 'upstream extractor failed'
    }));
    process.exit(1);
  }

  const data = result.data || {};
  console.log(JSON.stringify({
    ok: true,
    account_name: data.account_name || '',
    account_alias: data.account_alias || '',
    account_id: data.account_id || '',
    account_biz: data.account_biz || '',
    account_qr_code: data.account_qr_code || '',
    msg_title: data.msg_title || '',
    msg_link: data.msg_link || url,
    msg_mid: data.msg_mid || '',
    msg_idx: data.msg_idx || '',
    msg_sn: data.msg_sn || ''
  }));
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
