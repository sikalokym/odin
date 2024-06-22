<template>
  <div id="app">
    <NavBar />
    <div class="editor">
      <RouterView></RouterView>
    </div>
  </div>
</template>

<script>
import NavBar from './components/shared/NavBar.vue';
import { usePNOStore } from './stores/pno.js'
import { useEntitiesStore } from './stores/entities.js'
import { useAuthStore } from './stores/auth.js'

export default {
  name: 'App',
  components: {
    NavBar
  },
  async mounted() {
    
    const pnoStore = usePNOStore()
    const entitiesStore = useEntitiesStore()
    const authStore = useAuthStore()

    let countries = []
    for (let i = 0; i < 100; i++) {
      let user_allowed_countries = authStore.getCountriesRoles()
      
      if (user_allowed_countries === null  || user_allowed_countries === undefined || user_allowed_countries.length === 0) {
        await new Promise(resolve => setTimeout(resolve, 200))
        continue
      }
      user_allowed_countries = user_allowed_countries.map((country) => country.country)
      countries = await entitiesStore.fetchSupportedCountries(user_allowed_countries)
      if (countries === null || countries === undefined || countries.length === 0) {
        continue
      }
      if (i === 99) {
        new Promise(resolve => setTimeout(resolve, 5000))
      }
      break
    }
    if (countries === null || countries === undefined || countries.length === 0) {
      return
    }
    await pnoStore.setCountries(countries)
    await pnoStore.fetchAvailableModelYears()
    await entitiesStore.fetchModels()
    await entitiesStore.fetchEngines()
    await entitiesStore.fetchSalesversions()
    await entitiesStore.fetchGearboxes()
  },
};
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0%;
}

.editor {
  height: 100%;
  display: flex;
}
</style>