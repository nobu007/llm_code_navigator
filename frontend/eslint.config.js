const { FlatCompat } = require('@eslint/eslintrc')
const js = require('@eslint/js')
const tsPlugin = require('@typescript-eslint/eslint-plugin')
const tsParser = require('@typescript-eslint/parser')
const importPlugin = require('eslint-plugin-import')

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
})

module.exports = [
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
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling'], 'object', 'type', 'index'],
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
    files: ['*.config.js', '*.config.cjs', '*.config.ts'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
]
