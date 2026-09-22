import js from '@eslint/js';
import eslintPluginReact from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default [
  { ignores: ['dist', 'coverage'] },
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
      parser: tsParser,
      parserOptions: {
        projectService: {
          allowDefaultProject: ['playwright.config.ts', 'e2e/*.ts'],
        },
        tsconfigRootDir: import.meta.dirname,
      },

    },
    plugins: {
      react: eslintPluginReact,
      '@typescript-eslint': tseslint,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...tseslint.configs['recommended-type-checked'].rules,
      ...eslintPluginReact.configs.recommended.rules,
      ...eslintPluginReact.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
    settings: {
      react: { version: 'detect' },
    },
  },
  {
    files: ['**/*.{test,spec}.{ts,tsx}'],
    languageOptions: {
      globals: globals.vitest,
    },
  },
  {
    files: ['**/*.{js,mjs,cjs}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.node,
    },
  },
];
