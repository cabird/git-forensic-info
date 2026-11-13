#!/usr/bin/env node
// Print dist/primer.html and dist/cheat-sheet.html to PDF with headless Chromium.
// This step is optional and separate from build.py. It needs Node and Playwright
// (`npm install playwright`, then `npx playwright install chromium` if needed).
//
//   python3 build.py && node make_pdf.js [Letter|A4]        (default: Letter)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const format = process.argv[2] || 'Letter';
const dist = path.join(__dirname, 'dist');
const footer =
  '<div style="width:100%; font:8px sans-serif; color:#555; text-align:center;">' +
  '<span class="title"></span> &nbsp;&middot;&nbsp; <span class="pageNumber"></span> / ' +
  '<span class="totalPages"></span></div>';

// Chromium stamps the time of printing into the file. Pin it (same length, so
// the file's internal offsets stay valid) so the same HTML gives the same PDF.
const pinDates = (buf) => Buffer.from(
  buf.toString('latin1').replace(/(\/(?:CreationDate|ModDate) \(D:)\d{14}/g, '$120240101000000'),
  'latin1');

(async () => {
  const browser = await chromium.launch();
  const jobs = [
    { name: 'primer', options: { displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer } },
    { name: 'cheat-sheet', options: {} },
  ];
  for (const { name, options } of jobs) {
    const page = await browser.newPage();
    await page.goto('file://' + path.join(dist, name + '.html'));
    const pdf = await page.pdf({ format, printBackground: true, ...options });
    fs.writeFileSync(path.join(dist, name + '.pdf'), pinDates(pdf));
    console.log(`wrote dist/${name}.pdf (${format}, ${Math.round(pdf.length / 1024)} KB)`);
    await page.close();
  }
  await browser.close();
})();
