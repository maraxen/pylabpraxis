import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider } from '@chakra-ui/react';
import { Provider as ReduxProvider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store';
import { App } from './App';
import { system } from './theme';
import { OidcProvider } from "./oidc";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <OidcProvider
      ErrorFallback={({ initializationError }) => (
        <h1 style={{ color: "red" }}>
          An error occurred while initializing the OIDC client:
          {initializationError.message}
          {initializationError.type} /* "server down" | "bad configuration" | "unknown"; */
        </h1>
      )}
    >
      <BrowserRouter>
        <ReduxProvider store={store}>
          <ChakraProvider value={system}>
            <App />
          </ChakraProvider>
        </ReduxProvider>
      </BrowserRouter>
    </OidcProvider>
  </React.StrictMode >,
);