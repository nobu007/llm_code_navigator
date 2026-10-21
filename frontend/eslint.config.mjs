import { FlatCompat } from '@eslint/eslintrc';
import importPlugin from 'eslint-plugin-import';
import tsParser from '@typescript-eslint/parser';

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname,
});

const eslintConfig = [
  {
    ignores: ['node_modules/**', '.next/**', 'out/**', 'coverage/**'],
  },
  ...compat.extends('next/core-web-vitals', 'prettier'),
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
    },
    plugins: {
      import: importPlugin,
    },
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
          alphabetize: {
            order: 'asc',
          },
        },
      ],
    },
  },
];

export default eslintConfig;
