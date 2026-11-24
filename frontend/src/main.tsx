import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from './App';
import { SessaoProvider } from './components/auth/SessaoProvider';
import './index.css';

const rootElement = document.getElementById('root');

if (rootElement === null) {
  throw new Error('Elemento raiz #root não encontrado.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <SessaoProvider>
      <App />
    </SessaoProvider>
  </React.StrictMode>,
);
