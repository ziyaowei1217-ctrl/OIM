import express from 'express';
import cors from 'cors';
import multer from 'multer';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdfParse = require('pdf-parse');
import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ storage: multer.memoryStorage() });

// Initialize Gemini Client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

app.post('/api/match', upload.array('files'), async (req, res) => {
  try {
    const { outline } = req.body;
    const files = req.files as Express.Multer.File[];

    if (!outline) {
      return res.status(400).json({ error: 'Outline is required' });
    }

    if (!files || files.length === 0) {
      return res.status(400).json({ error: 'At least one PDF file is required' });
    }

    // Parse all PDFs
    const parsedDocuments = [];
    for (const file of files) {
      const data = await pdfParse(file.buffer);
      parsedDocuments.push({
        filename: file.originalname,
        content: data.text,
      });
    }

    // Construct the prompt for Gemini
    const prompt = `
You are a research assistant. Below is an Outline for a paper and the text from several source documents.
Your task is to extract relevant quotes from the source documents that map to each section of the Outline.

Outline:
${outline}

Sources:
${parsedDocuments.map(doc => `--- Source: ${doc.filename} ---\n${doc.content}\n`).join('\n')}

Please return ONLY a valid JSON array matching the structure below. Do not wrap in markdown \`\`\`json.
[
  {
    "id": "section_identifier",
    "label": "Section Title (e.g., I. Introduction)",
    "quotes": [
      {
        "text": "The exact quote text from the source",
        "source": "Filename of the source",
        "page": "Approximate page number or 'N/A'"
      }
    ]
  }
]
`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      }
    });

    const resultText = response.text || "[]";
    let jsonResult;
    try {
      jsonResult = JSON.parse(resultText);
    } catch (e) {
        console.error("Failed to parse Gemini response as JSON:", resultText);
        const cleanText = resultText.replace(/```json/g, '').replace(/```/g, '').trim();
        jsonResult = JSON.parse(cleanText);
    }

    res.json(jsonResult);
  } catch (error: any) {
    console.error('API Error:', error);
    res.status(500).json({ error: error.message || 'An error occurred during matching.' });
  }
});

app.post('/api/generate-outline', async (req, res) => {
  try {
    const { description } = req.body;
    if (!description) {
      return res.status(400).json({ error: 'Description is required' });
    }

    const prompt = `
You are a professional academic writing assistant.
Your task is to create a structured outline for a paper based on the following description.

Description:
${description}

Please return ONLY a valid JSON object matching the structure below. Do not wrap in markdown \`\`\`json.
{
  "title": "A good, professional paper title based on the description",
  "outline": "A full, structured outline with Roman numerals (I, II, III...) containing sections and key themes, mimicking an academic paper outline."
}
`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      }
    });

    const resultText = response.text || "{}";
    let jsonResult;
    try {
      jsonResult = JSON.parse(resultText);
    } catch (e) {
      console.error("Failed to parse Gemini response as JSON:", resultText);
      const cleanText = resultText.replace(/```json/g, '').replace(/```/g, '').trim();
      jsonResult = JSON.parse(cleanText);
    }

    res.json(jsonResult);
  } catch (error: any) {
    console.error('API Error:', error);
    res.status(500).json({ error: error.message || 'An error occurred during outline generation.' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
