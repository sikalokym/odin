import msalInstance from './authConfig';

export const login = async () => {
    try {
        await msalInstance.loginPopup({
            scopes: ['user.read'],
        });
        const account = msalInstance.getAllAccounts()[0];
        msalInstance.setActiveAccount(account);
    } catch (error) {
        console.error(error);
    }
};

export const getRoles = async () => {

    const account = msalInstance.getActiveAccount();
    if (!account) {
        console.error('No active account found');
        return [];
    }

    const accessToken = await msalInstance.acquireTokenSilent({
        scopes: ['user.read'],
        account,
    });

    const userRoles = accessToken.idTokenClaims.roles || [];
    console.log(`User roles: ${userRoles}`);
    return userRoles;
};
