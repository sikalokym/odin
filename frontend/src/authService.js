import msalInstance from './authConfig';
import { useAuthStore } from './stores/auth';

export const login = async () => {
    try {
        const loginResponse = await msalInstance.loginPopup({
            scopes: ['User.Read', 'Group.Read.All'],
        });
        msalInstance.setActiveAccount(loginResponse.account);
    } catch (error) {
        console.error('Login failed:', error);
    }
};

export const fetchCountriesRoles = async () => {

    const account = msalInstance.getActiveAccount();
    if (!account) {
        throw new Error('No active account found');
    }

    const tokenResponse = await msalInstance.acquireTokenSilent({
        scopes: ['User.Read', 'Group.Read.All'],
        account,
    });
    const userRoles = tokenResponse.idTokenClaims.roles || [];
    if (tokenResponse.accessToken) {
        try {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${tokenResponse.accessToken}`);
            headers.append('Content-Type', 'application/json');

            const response = await fetch('https://graph.microsoft.com/v1.0/me/memberOf', { headers });
            const data = await response.json();

            if (response.ok) {
                let groups = parseGroupNames(data.value.filter(g => g.displayName.startsWith('odin-')).map(group => group.displayName));
                for (let group of groups) {
                    if (!userRoles.includes(group.role)) {
                        group = null;
                    }
                }
                groups = groups.filter(Boolean);
                useAuthStore().assignCountriesRoles(groups);
            } else {
                throw new Error('Failed to fetch group data');
            }
        } catch (error) {
            console.error('Error fetching group data:', error);
            return [];
        }
    }
};

export const parseGroupNames = (groups) => {
    return groups.map(group => {
        const match = group.match(/odin-(\w+)-(\w+)/);
        return match ? { country: match[1], role: match[2] } : null;
    }).filter(Boolean);
};

export const ensureAuthenticated = async () => {
    if (!msalInstance.getActiveAccount()) {
        await login();
    }
    await fetchCountriesRoles();
};
