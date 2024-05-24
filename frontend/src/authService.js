import msalInstance from './authConfig';

export const login = async () => {
    try {
        const loginResponse = await msalInstance.loginPopup({
            scopes: ['user.read'],
        });
        msalInstance.setActiveAccount(loginResponse.account);
    } catch (error) {
        console.error('Login failed:', error);
    }
};

export const getRoles = async () => {

    const account = msalInstance.getActiveAccount();
    if (!account) {
        throw new Error('No active account found');
    }
    console.log('account', account);

    const tokenResponse = await msalInstance.acquireTokenSilent({
        scopes: ['user.read'],
        account,
    });

    const userRoles = tokenResponse.idTokenClaims.roles || [];
    console.log('userRoles', userRoles);
    return userRoles;
};

export const ensureAuthenticated = async () => {
    if (!msalInstance.getActiveAccount()) {
        await login();
    }
};
