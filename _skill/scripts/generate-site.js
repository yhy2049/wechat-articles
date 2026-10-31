#!/usr/bin/env node
/* 重建 .github-pages：文章 md/html、年份页、首页统计、API JSON
 * 用法：node _skill/scripts/generate-site.js
 * 站点以年份目录为准做镜像：年份目录里没有的文章会从站点移除。
 */
const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

const ROOT = path.resolve(__dirname, '..', '..');
const SITE = path.join(ROOT, '.github-pages');
const YEARS = fs.readdirSync(ROOT)
  .filter(d => /^\d{4}$/.test(d) && fs.statSync(path.join(ROOT, d)).isDirectory())
  .filter(d => fs.readdirSync(path.join(ROOT, d)).some(f => f.endsWith('.md')))
  .sort();

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const norm = s => s.replace(/[\s「」『』【】《》〈〉（）()\[\]·—–―…、，。！!？?：:;；,.|\\/<>:*"'‘’“”~`#@$%^&=_+\-｜／＼－　]/g, '');
const now = new Date();
const cst = new Date(now.getTime() + 8 * 3600 * 1000);
const stamp = cst.toISOString().slice(0, 16).replace('T', ' ');
const iso = now.toISOString();

function parseArticle(file) {
  const base = path.basename(file, '.md');
  const raw = fs.readFileSync(file, 'utf8');
  let text = raw;
  const fallback = base.slice(11);
  let title = fallback;
  // 正文自带与文件名同名的 H1 时，用它作正式标题（保留书名号等），并从正文移除
  const lines = text.split('\n');
  for (let i = 0; i < Math.min(lines.length, 10); i++) {
    const m = lines[i].match(/^#\s+(.+?)\s*$/);
    if (m && norm(m[1]) === norm(fallback)) {
      title = m[1];
      lines.splice(i, 1);
      text = lines.join('\n');
      break;
    }
  }
  return { id: base, title, date: base.slice(0, 10), year: base.slice(0, 4), file, text, rawLength: raw.length };
}

const articles = [];
for (const y of YEARS) {
  const dir = path.join(ROOT, y);
  for (const f of fs.readdirSync(dir)) {
    if (f.endsWith('.md')) articles.push(parseArticle(path.join(dir, f)));
  }
}
articles.sort((a, b) => (b.date + b.id).localeCompare(a.date + a.id, 'zh'));
const live = new Set(articles.map(a => a.id));

// 1. 站点镜像：年份目录已不存在的文章从站点删除
let cleaned = 0;
for (const y of YEARS) {
  const dir = path.join(SITE, 'articles', y);
  if (!fs.existsSync(dir)) continue;
  for (const f of fs.readdirSync(dir)) {
    const id = f.replace(/\.(md|html)$/, '');
    if (!live.has(id)) { fs.unlinkSync(path.join(dir, f)); cleaned++; }
  }
}

// 2. 同步 md
let copied = 0;
for (const a of articles) {
  const dir = path.join(SITE, 'articles', a.year);
  fs.mkdirSync(dir, { recursive: true });
  const dest = path.join(dir, a.id + '.md');
  if (!fs.existsSync(dest)) { fs.copyFileSync(a.file, dest); copied++; }
}

// 3. 生成文章 HTML（取最新的现有页面当模板）
const template = (() => {
  for (const y of [...YEARS].reverse()) {
    const dir = path.join(SITE, 'articles', y);
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort().reverse();
    for (const f of files) {
      const text = fs.readFileSync(path.join(dir, f), 'utf8');
      if (text.includes('<div class="article-content">') && text.includes('<div class="footer">')) return text;
    }
  }
  throw new Error('未找到可用的文章 HTML 模板');
})();
const startMark = '<div class="article-content">';
const startIdx = template.indexOf(startMark) + startMark.length;
const closeIdx = template.lastIndexOf('</div>', template.indexOf('<div class="footer">'));
const tplPrefix = template.slice(0, startIdx);
const tplSuffix = template.slice(closeIdx);

function renderArticle(a) {
  let body = marked.parse(a.text, { headerIds: false, mangle: false });
  body = body.replace(/<img\s/g, '<img referrerpolicy="no-referrer" ');
  // 存档里的原文链接块改成单行样式，避免两端对齐拉大字距
  body = body.replace(
    /<blockquote>\s*<p>公众号原文：<a href="([^"]+)">[^<]*<\/a><\/p>\s*<\/blockquote>/,
    (m, url) => `<p class="article-source" style="text-align:left;font-size:0.9em;color:#8a8a8a;margin:18px 0;word-break:break-all;">公众号原文：<a href="${url}" target="_blank" rel="noopener">查看原文 ↗</a></p>`
  );
  const p = tplPrefix
    .replace(/<title>[\s\S]*?<\/title>/, `<title>${esc(a.title)} - 24帧公众号存档</title>`)
    .replace(/<div class="article-date">.*?<\/div>/, `<div class="article-date">📅 ${a.date}</div>`)
    .replace(/<h1 class="article-title">[\s\S]*?<\/h1>/, `<h1 class="article-title">${esc(a.title)}</h1>`)
    .replace(/(<a href="\.\.\/\.\.\/)\d{4}(\.html">← )\d{4}(年<\/a>)/, `$1${a.year}$2${a.year}$3`);
  return p + '\n      ' + body + '\n\n    ' + tplSuffix;
}

let htmlMade = 0;
for (const a of articles) {
  const dest = path.join(SITE, 'articles', a.year, a.id + '.html');
  if (fs.existsSync(dest) && fs.statSync(dest).mtimeMs >= fs.statSync(a.file).mtimeMs) continue;
  fs.writeFileSync(dest, renderArticle(a));
  htmlMade++;
}

// 4. 年份页
for (const y of YEARS) {
  const pageFile = path.join(SITE, y + '.html');
  if (!fs.existsSync(pageFile)) continue;
  const list = articles.filter(a => a.year === y);
  const items = list.map(a =>
    `      <li>\n        <a href="articles/${y}/${a.id}.html" class="article-item">\n` +
    `          <div class="date">${a.date}</div>\n          <div class="title">${esc(a.title)}</div>\n        </a>\n      </li>`
  ).join('\n');
  let html = fs.readFileSync(pageFile, 'utf8');
  html = html.replace(/(<ul class="article-list" id="articleList">)[\s\S]*?(\n    <\/ul>)/, `$1\n${items}$2`);
  html = html.replace(/<p class="count">共 \d+ 篇<\/p>/, `<p class="count">共 ${list.length} 篇</p>`);
  fs.writeFileSync(pageFile, html);
}

// 5. 首页统计
{
  const file = path.join(SITE, 'index.html');
  let html = fs.readFileSync(file, 'utf8');
  const counts = YEARS.map(y => articles.filter(a => a.year === y).length);
  let i = 0;
  html = html.replace(/(<div class="stat-value">)\d+(<\/div>)/g, (m, a, b) => `${a}${[articles.length, ...counts][i++]}${b}`);
  let j = 0;
  html = html.replace(/(<div class="count">)\d+( 篇<\/div>)/g, (m, a, b) => `${a}${counts[j++]}${b}`);
  html = html.replace(/生成时间: [\d-]+ [\d:]+/, `生成时间: ${stamp}`);
  fs.writeFileSync(file, html);
}

// 6. API
const apiDir = path.join(SITE, 'api');
const toEntry = a => ({
  id: a.id, title: a.title, date: a.date, year: a.year,
  url: `articles/${a.year}/${a.id}.md`,
});
const yearStats = {};
let totalChars = 0;
for (const a of articles) totalChars += a.rawLength;
for (const y of YEARS) {
  const list = articles.filter(a => a.year === y);
  yearStats[y] = list.length;
  fs.writeFileSync(path.join(apiDir, y + '.json'), JSON.stringify({ generated_at: iso, year: y, total: list.length, articles: list.map(toEntry) }, null, 2));
}
fs.writeFileSync(path.join(apiDir, 'index.json'), JSON.stringify({ generated_at: iso, total: articles.length, articles: articles.map(toEntry) }, null, 2));
fs.writeFileSync(path.join(apiDir, 'stats.json'), JSON.stringify({
  generated_at: iso,
  total_articles: articles.length,
  total_characters: totalChars,
  average_characters: Math.round(totalChars / articles.length),
  years: yearStats,
  year_range: { first: articles[articles.length - 1].date, last: articles[0].date },
}, null, 2));

// 7. api.html 数字
{
  const file = path.join(SITE, 'api.html');
  if (fs.existsSync(file)) {
    let html = fs.readFileSync(file, 'utf8');
    const latest = YEARS[YEARS.length - 1];
    html = html.replace(/("total_articles"<\/span>: <span class="number">)\d+/, `$1${articles.length}`);
    html = html.replace(/("total"<\/span>: <span class="number">)\d+/, `$1${articles.length}`);
    html = html.replace(new RegExp(`("${latest}"</span>: <span class="number">)\\d+`), `$1${yearStats[latest]}`);
    html = html.replace(/生成时间: [\d-]+ [\d:]+/, `生成时间: ${stamp}`);
    fs.writeFileSync(file, html);
  }
}

console.log(JSON.stringify({
  articles: articles.length,
  byYear: yearStats,
  removedFiles: cleaned,
  mdCopied: copied,
  htmlGenerated: htmlMade,
  totalChars,
  range: [articles[articles.length - 1].date, articles[0].date],
}, null, 2));
