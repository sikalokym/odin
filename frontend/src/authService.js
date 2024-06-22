import msalInstance from './authConfig';
import { useAuthStore } from './stores/auth';

let isInteractionInProgress = false;

export const login = async () => {
    if (isInteractionInProgress) {
        console.error('Login interaction already in progress');
        return;
    }
    isInteractionInProgress = true;
    // const popupLoginResponse = await msalInstance.loginPopup({
    //     scopes: ['User.Read', 'Group.Read.All'],
    // });
    // msalInstance.setActiveAccount(loginResponse.account);
    msalInstance.loginRedirect({
        scopes: ['User.Read', 'Group.Read.All'],
    }).then(response => {
        isInteractionInProgress = false;
    }).catch(error => {
        console.error('Login failed:', error);
        isInteractionInProgress = false;
    });
};

export const fetchCountriesRoles = async () => {
    const account = msalInstance.getActiveAccount();
    if (!account) {
        throw new Error('No active account found');
    }

    try {
        const tokenResponse = await msalInstance.acquireTokenSilent({
            scopes: ['User.Read', 'Group.Read.All'],
            account,
        });

        const userRoles = tokenResponse.idTokenClaims.roles || [];
        if (tokenResponse.accessToken) {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${tokenResponse.accessToken}`);
            headers.append('Content-Type', 'application/json');

            const response = await fetch('https://graph.microsoft.com/v1.0/me/memberOf', { headers });
            const data = await response.json();
            
            if (response.ok) {
                let groups = parseGroupNames(data.value.filter(g => g.displayName.startsWith('odin-')).map(group => group.displayName));
                groups = groups.filter(group => userRoles.includes(group.role));
                
                useAuthStore().assignCountriesRoles(groups);
            } else {
                throw new Error('Failed to fetch group data');
            }
        }
    } catch (error) {
        console.error('Token acquisition error:', error);
        if ((error.errorCode === 'monitor_window_timeout' || error.errorCode === 'interaction_required') && !isInteractionInProgress) {
            try {
                isInteractionInProgress = true;
                const tokenResponse = await msalInstance.acquireTokenPopup({
                    scopes: ['User.Read', 'Group.Read.All'],
                    account,
                });

                const userRoles = tokenResponse.idTokenClaims.roles || [];
                if (tokenResponse.accessToken) {
                    const headers = new Headers();
                    headers.append('Authorization', `Bearer ${tokenResponse.accessToken}`);
                    headers.append('Content-Type', 'application/json');

                    const response = await fetch('https://graph.microsoft.com/v1.0/me/memberOf', { headers });
                    const data = await response.json();

                    if (response.ok) {
                        let groups = parseGroupNames(data.value.filter(g => g.displayName.startsWith('odin-')).map(group => group.displayName));
                        groups = groups.filter(group => userRoles.includes(group.role));
                        useAuthStore().assignCountriesRoles(groups);
                    } else {
                        throw new Error('Failed to fetch group data');
                    }
                }
            } catch (popupError) {
                console.error('Token acquisition via popup failed:', popupError);
                isInteractionInProgress = false;
                return [];
            } finally {
                isInteractionInProgress = false;
            }
        } else {
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
    else {
        await fetchCountriesRoles();
    }
    
};
