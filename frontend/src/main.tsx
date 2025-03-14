import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChakraProvider } from '@chakra-ui/react';
import { Provider as ReduxProvider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store';
import { App } from './App';
import { system } from '@/styles/theme';
import { OidcProvider } from "./oidc";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <OidcProvider
      ErrorFallback={({ initializationError }) => (
        <h1 style={{ color: "red" }}>
          {initializationError.isAuthServerLikelyDown ? (
            <>Sorry our authentication server is currently down, please try again later</>
          ) : (
            // NOTE: Check initializationError.message for debug information.
            // It's an error on your end no need to show it to the user.
            <>Unexpected authentication error </>
          )}
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