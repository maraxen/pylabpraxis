import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider } from '@chakra-ui/react';
import { Provider as ReduxProvider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store';
import { App } from './App';
import { system } from './theme';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ReduxProvider store={store}>
        <ChakraProvider value={system}>
          <App />
        </ChakraProvider>
      </ReduxProvider>
    </BrowserRouter>
  </React.StrictMode>,
);