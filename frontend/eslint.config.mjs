import { fileURLToPath } from 'node:url';

import { FlatCompat } from '@eslint/eslintrc';
import js from '@eslint/js';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import importPlugin from 'eslint-plugin-import';

const compat = new FlatCompat({
  baseDirectory: fileURLToPath(new URL('.', import.meta.url)),
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

const config = [
  ...compat.extends(
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'next/core-web-vitals',
    'prettier'
  ),
  {
    languageOptions: {
      parser: tsParser,
    },
    plugins: { '@typescript-eslint': tsPlugin, import: importPlugin },
    rules: {
      'import/order': [
        'error',
        {
          groups: [
            'builtin',
            'external',
            'internal',
            ['parent', 'sibling'],
            'object',
            'type',
            'index',
          ],
          'newlines-between': 'always',
          pathGroupsExcludedImportTypes: ['builtin'],
          pathGroups: [
            { pattern: '@/utils/**', group: 'internal', position: 'before' },
            { pattern: '@/libs/**', group: 'internal', position: 'before' },
            { pattern: '@/hooks/**', group: 'internal', position: 'before' },
            { pattern: '@/components/**', group: 'internal', position: 'before' },
            { pattern: '@/const/**', group: 'internal', position: 'before' },
            { pattern: '@/types/**', group: 'internal', position: 'before' },
          ],
          alphabetize: { order: 'asc' },
        },
      ],
    },
  },
  {
    // Build/tooling config files are CommonJS and load plugins with require().
    files: ['*.config.js', '*.config.cjs', '*.config.mjs', '*.config.ts'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
];

export default config;
