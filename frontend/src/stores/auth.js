// Author: Hassan Wahba

import { defineStore } from 'pinia'

export const useAuthStore = defineStore({
    id: 'auth',
    state: () => ({
      supported_countries_roles: [],
    }),
    actions: {
      assignCountriesRoles(countries_roles) {
        this.supported_countries_roles = countries_roles
      },
      getCountriesRoles() {
        return this.supported_countries_roles
      }
    }
})
