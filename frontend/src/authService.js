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
    return ['Modifier'];

    // Simulate roles for testing purposes
    //   const urlParams = new URLSearchParams(window.location.search);
    //   const testRole = urlParams.get('role');
    //   if (testRole) {
    //     return [testRole];
    //   }

    const account = msalInstance.getActiveAccount();
    if (!account) {
        throw new Error('No active account found');
    }

    const tokenResponse = await msalInstance.acquireTokenSilent({
        scopes: ['user.read'],
        account,
    });

    const userRoles = tokenResponse.idTokenClaims.roles || [];
    return userRoles;
};

export const ensureAuthenticated = async () => {
    return;
    if (!msalInstance.getActiveAccount()) {
        await login();
    }
};
