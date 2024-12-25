// Author: Hassan Wahba

import { PublicClientApplication } from '@azure/msal-browser';

let redirectUri = window.location.origin;

const msalConfig = {
    auth: {
        clientId: process.env.VUE_APP_CLIENT_ID,
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
