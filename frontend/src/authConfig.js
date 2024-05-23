import { PublicClientApplication } from '@azure/msal-browser';

let redirectUri = '';
if (process.env.NODE_ENV === 'development') {
    redirectUri = 'http://localhost:8080';
} else {
    redirectUri = 'https://pmt-portal.azurewebsites.net';
}

const msalConfig = {
    auth: {
        clientId: 'c507abc7-3ac1-4fd8-8f62-461b88d61f48',
        authority: 'https://login.microsoftonline.com/81fa766e-a349-4867-8bf4-ab35e250a08f',
        redirectUri: redirectUri,
    },
    cache: {
        cacheLocation: 'localStorage',
        storeAuthStateInCookie: true,
    },
};

const msalInstance = new PublicClientApplication(msalConfig);
export const initializeMsal = async () => {
    await msalInstance.initialize();
  };

export default msalInstance;
