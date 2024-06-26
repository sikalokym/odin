import msalInstance from './authConfig';
import { useAuthStore } from './stores/auth';

let isInteractionInProgress = false;

export const login = async () => {
    if (isInteractionInProgress) {
        console.error('Login interaction already in progress');
        return;
    }
    isInteractionInProgress = true;
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
    console.log('Fetching countries roles, account:', account);
    try {
        const tokenResponse = await msalInstance.acquireTokenSilent({
            scopes: ['User.Read', 'Group.Read.All'],
            account,
        });
        console.log('Token acquired:', tokenResponse);
        const userRoles = tokenResponse.idTokenClaims.roles || [];
        if (tokenResponse.accessToken) {
            let groups = await fetchAllGroups(tokenResponse);
            console.log('Fetched groups:', groups);
            console.log('Mapped groups:', groups.filter(group => group.displayName.startsWith('odin-')).map(group => group.displayName));
            let parsedGroups = parseGroupNames(groups.filter(group => group.displayName.startsWith('odin-')).map(group => group.displayName));
            console.log('Parsed groups:', parsedGroups);
            groups = parsedGroups.filter(group => userRoles.includes(group.role));
            console.log('Filtered groups:', groups);
            useAuthStore().assignCountriesRoles(groups);
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
export async function fetchAllGroups(tokenResponse) {
    let allGroups = [];
    let nextLink = 'https://graph.microsoft.com/v1.0/me/memberOf';
  
    while (nextLink) {
      const headers = new Headers();
      headers.append('Authorization', `Bearer ${tokenResponse.accessToken}`);
      headers.append('Content-Type', 'application/json');
  
      const response = await fetch(nextLink, { headers });
      const data = await response.json();
  
      if (data.value) {
        allGroups = allGroups.concat(data.value);
      }
  
      nextLink = data['@odata.nextLink'];
    }
  
    return allGroups;
  }

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
