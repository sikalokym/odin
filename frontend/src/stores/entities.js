import { defineStore } from 'pinia'
import index from '../api/index.js'

export const useEntitiesStore = defineStore({
  id: 'entities',
  state: () => ({
    models: [],
    engines: [],
    salesversions: [],
    gearboxes: [],
    countries: [],
    country: '',
    model_year: new Date().getFullYear() + 1,
  }),
  actions: {
    setCountry(newCountryName) {
        let newCountry = this.countries.find(country => country.CountryText === newCountryName).Code
        this.country = newCountry;
        return newCountry
    },
    setModelYear(newModelYear) {
        this.model_year = newModelYear;
    },
    async fetchSupportedCountries() {
      let path = `/setup/supported_countries`
      return index.get(path).then((response) => {
        this.countries = response.data
        this.country = this.countries[0].Code
        console.log("Available countries fetched")
        return this.country
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchModels() {
        let model_year = "0000"
        if (this.model_year !== '0') {
            model_year = this.model_year
        }
        let path = `/db/${this.country}/${model_year}/models`
        return await index.get(path).then((response) => {
            this.models = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    async fetchEngines() {
        let model_year = "0000"
        if (this.model_year !== '0') {
            model_year = this.model_year
        }
        let path = `/db/${this.country}/${model_year}/engines`
        return await index.get(path).then((response) => {
            this.engines = response.data
        }).catch((error) => {
            console.log(error)
        })
        },
    async fetchSalesversions() {
        let model_year = "0000" 
        if (this.model_year !== '0') {
            model_year = this.model_year
        }
        let path = `/db/${this.country}/${model_year}/sales_versions`
        return await index.get(path).then((response) => {
            this.salesversions = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    async fetchGearboxes() {
        let model_year = "0000"
        if (this.model_year !== '0') {
            model_year = this.model_year
        }
        let path = `/db/${this.country}/${model_year}/gearboxes`
        return await index.get(path).then((response) => {
            this.gearboxes = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    async fetchCountries() {
        let path = `/setup/supported_countries`
        return await index.get(path).then((response) => {
            this.countries = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    // Database Updates
    async pushUpdateModel(model, translation) {
        let updates = {
            Code: model,
            CountryText: translation,
        }
        let path = `/db/${this.country}/${this.model_year}/write/models`
        return index.post(path, updates);
    },
    async pushUpdateEngine(engine, translation, enginecategory, enginetype, performance) {
        let updates = {
            Code: engine,
            CountryText: translation,
            EngineCategory: enginecategory,
            EngineType: enginetype,
            Performance: performance
        }
        let path = `/db/${this.country}/${this.model_year}/write/engines`
        return index.post(path, updates);
    },
    async pushUpdateSV(salesversion, translation) {
        let updates = {
            Code: salesversion,
            CountryText: translation,
        }
        let path = `/db/${this.country}/${this.model_year}/write/sales_versions`
        return index.post(path, updates);
    },
    async pushUpdateGearbox(gearbox, translation) {
        let updates = {
            Code: gearbox,
            CountryText: translation,
        }
        let path = `/db/${this.country}/${this.model_year}/write/gearboxes`
        return index.post(path, updates);
    },
},
})
