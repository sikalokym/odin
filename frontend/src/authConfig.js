// Author: Hassan Wahba

import { PublicClientApplication } from '@azure/msal-browser';

let redirectUri = '';
if (process.env.NODE_ENV === 'development') {
    redirectUri = 'http://localhost:8080';
} else {
    redirectUri = 'https://odin-portal.azurewebsites.net';
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
    msalInstance.handleRedirectPromise()
    .then((response) => {
        if (response !== null) {
            console.log("Login Successful", response);

            // Set the active account
            msalInstance.setActiveAccount(response.account);
        } else {
            // No login response, check if an active account is already set
            const account = msalInstance.getActiveAccount();
            if (account) {
                console.log("Active account: ", account);
            } else {
                console.log("No active account");
            }
        }
    })
    .catch((error) => {
        console.error("Login Error", error);
    });
  };

export default msalInstance;
