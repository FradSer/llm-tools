#!/usr/bin/env bun
import { createReadStream, createWriteStream } from 'fs';
import sax from 'sax';
import { parseArgs } from 'util';

interface TMXRecord {
  source: string;
  target: string;
}

interface ProgramOptions {
  input: string;
  output: string;
  debug: boolean;
  limit?: number;
  silent?: boolean;
}

// Parse command line arguments
function parseArguments(): ProgramOptions {
  const { values } = parseArgs({
    options: {
      input: {
        type: 'string',
        short: 'i',
      },
      output: {
        type: 'string',
        short: 'o',
      },
      debug: {
        type: 'boolean',
        short: 'd',
        default: false,
      },
      limit: {
        type: 'string',
        short: 'l',
      },
      silent: {
        type: 'boolean',
        short: 's',
        default: false,
      },
    },
  });

  if (!values.input || !values.output) {
    console.error('Usage: bun run index.ts --input <tmx-file> --output <jsonl-file> [--debug] [--limit <number>] [--silent]');
    process.exit(1);
  }

  return {
    input: values.input,
    output: values.output,
    debug: values.debug || false,
    limit: values.limit ? parseInt(values.limit, 10) : undefined,
    silent: values.silent || false,
  };
}

function cleanText(text: string): string {
  return text
    .replace(/\s+/g, ' ')  // 规范化空白字符
    .replace(/[\r\n]+/g, ' ')  // 移除换行
    .replace(/\\n/g, ' ')  // 移除转义的换行
    .replace(/\t/g, ' ')   // 移除制表符
    .trim();
}

function isValidRecord(record: Partial<TMXRecord>): boolean {
  return Boolean(
    record.source && 
    record.target && 
    record.source.length > 0 && 
    record.target.length > 0
  );
}

async function convertTMXtoJSONL(options: ProgramOptions): Promise<void> {
  return new Promise((resolve, reject) => {
    const outputStream = createWriteStream(options.output, { encoding: 'utf8' });
    let currentRecord: Partial<TMXRecord> = {};
    let currentLang: string | null = null;
    let isInSeg = false;
    let recordCount = 0;
    let hasError = false;
    let isEnded = false;
    let lastProgressUpdate = Date.now();
    let fileSize = 0;
    let bytesRead = 0;
    
    // 获取文件大小
    try {
      const stats = Bun.file(options.input).size;
      fileSize = stats;
    } catch (error) {
      console.warn('Unable to get file size, progress will be based on record count only');
    }

    function updateProgress(record?: TMXRecord) {
      const now = Date.now();
      // 每100ms更新一次进度，避免过多输出
      if (now - lastProgressUpdate < 100 && !options.debug) return;
      lastProgressUpdate = now;

      // 清除当前行
      process.stdout.write('\r\x1b[K');

      // 显示进度
      const progress = fileSize ? Math.round((bytesRead / fileSize) * 100) : 0;
      const progressText = `Progress: ${recordCount.toLocaleString()} records`;
      const progressBar = fileSize ? ` [${progress}%]` : '';
      
      // 如果有最新记录，显示它
      if (record && !options.silent) {
        process.stdout.write(
          `\r${progressText}${progressBar} | Latest: ${record.source.slice(0, 30)}${record.source.length > 30 ? '...' : ''} => ${record.target.slice(0, 30)}${record.target.length > 30 ? '...' : ''}`
        );
      } else {
        process.stdout.write(`\r${progressText}${progressBar}`);
      }
    }

    // Create a relaxed parser
    const parser = sax.createStream(false, {
      trim: true,
      normalize: true,
      lowercase: true
    });

    // Handle parsing errors
    parser.on('error', (error: Error) => {
      if (!hasError) {
        console.error('Warning: XML parsing error (showing first only):', error.message);
        hasError = true;
      }
      // Continue parsing despite errors
      parser.resume();
    });

    // Handle opening tags
    parser.on('opentag', (node: sax.Tag) => {
      if (isEnded) return;
      
      if (node.name === 'tuv') {
        const attrs = node.attributes || {};
        const xmlLang = (attrs['xml:lang'] || attrs['lang'] || attrs['xmllang'] || attrs['language'])?.toString();
        currentLang = xmlLang ? xmlLang.toLowerCase() : null;
      } else if (node.name === 'seg') {
        isInSeg = true;
      }
    });

    // Handle text content
    parser.on('text', (text: string) => {
      if (isEnded) return;
      
      if (isInSeg && currentLang) {
        const cleanedText = cleanText(text);
        if (cleanedText) {
          if (currentLang === 'en') {
            currentRecord.source = (currentRecord.source || '') + cleanedText;
          } else if (currentLang === 'zh_cn') {
            currentRecord.target = (currentRecord.target || '') + cleanedText;
          }
        }
      }
    });

    // 更新已读取的字节数
    parser.on('text', function(text) {
      bytesRead += Buffer.byteLength(text);
    });

    // Handle closing tags
    parser.on('closetag', (tagName: string) => {
      if (isEnded) return;
      
      if (tagName === 'tu') {
        if (isValidRecord(currentRecord)) {
          const record = {
            source: cleanText(currentRecord.source!),
            target: cleanText(currentRecord.target!)
          };
          
          // Write to JSONL file with proper formatting
          outputStream.write(JSON.stringify(record).trim() + '\n');
          recordCount++;
          
          // Update progress
          updateProgress(record);
          
          // Debug output
          if (options.debug) {
            console.log(`\n[${recordCount}]`);
            console.log(`Source: ${record.source}`);
            console.log(`Target: ${record.target}`);
            console.log('----------------------------------------');
          }
          
          // Reset for next record
          currentRecord = {};
          
          // Stop if we've reached the limit
          if (options.limit && recordCount >= options.limit) {
            isEnded = true;
            cleanup();
          }
        }
      } else if (tagName === 'seg') {
        isInSeg = false;
      } else if (tagName === 'tuv') {
        currentLang = null;
      }
    });

    function cleanup() {
      parser.removeAllListeners();
      // 最后更新一次进度
      process.stdout.write('\n');
      outputStream.end(() => {
        if (recordCount > 0) {
          console.log(`\nSuccessfully converted ${recordCount.toLocaleString()} records to ${options.output}`);
          resolve();
        } else {
          reject(new Error('No valid records found in the TMX file'));
        }
      });
    }

    // Handle end of parsing
    parser.on('end', cleanup);

    // Start parsing
    if (options.debug) {
      console.log('Starting to parse TMX file...');
      console.log('----------------------------------------');
    }
    
    // Handle stream errors
    const stream = createReadStream(options.input, { encoding: 'utf8' });
    stream.on('error', (error: Error) => {
      console.error('Error reading file:', error);
      cleanup();
      reject(error);
    });
    
    stream.pipe(parser);
  });
}

// Execute the script
const options = parseArguments();
convertTMXtoJSONL(options).catch(error => {
  console.error('Script failed:', error);
  process.exit(1);
});
