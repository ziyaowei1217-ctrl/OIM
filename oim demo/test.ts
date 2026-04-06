import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');
import * as fs from 'fs';

async function testPdf() {
  try {
    console.log("pdfParse type:", typeof pdfParse);
    // Let's create a dummy pdf buffer. We can't really easily without a library, but let's just see if it's a function.
  } catch (error) {
    console.error("Test Error:", error);
  }
}

testPdf();
