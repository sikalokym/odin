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
    while (true) {
      let user_allowed_countries = authStore.getCountriesRoles()
      user_allowed_countries = user_allowed_countries.map((country) => country.country)
      countries = await entitiesStore.fetchSupportedCountries(user_allowed_countries)
      if (countries.length === 0) {
        console.log('No countries fetched, retrying in 500ms')
        await new Promise((resolve) => setTimeout(resolve, 500))
      } else {
        break
      }
    }
    console.log('Countries fetched', countries)
    await pnoStore.setCountries(countries)
    await pnoStore.fetchAvailableModelYears().then(() => {
      console.log('Available model years fetched')
    }).catch((error) => {
      console.error('Error fetching available model years', error)
    })

    await entitiesStore.fetchModels().then(() => {
      console.log('Model text fetched')
    }).catch((error) => {
      console.error('Error fetching model text', error)
    }),
    await entitiesStore.fetchEngines().then(() => {
      console.log('Engine text fetched')
    }).catch((error) => {
      console.error('Error fetching engine text', error)
    }),
    await entitiesStore.fetchSalesversions().then(() => {
      console.log('Salesversion text fetched')
    }).catch((error) => {
      console.error('Error fetching salesversion text', error)
    }),
    await entitiesStore.fetchGearboxes().then(() => {
      console.log('Gearboxes text fetched')
    }).catch((error) => {
      console.error('Error fetching gearboxes text', error)
    })
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