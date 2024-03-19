import { defineStore } from 'pinia'
import index from '../api/index.js'

export const useEntitiesStore = defineStore({
  id: 'entities',
  state: () => ({
    models: [],
    engines: [],
    salesversions: [],
    gearboxes: [],
    country: '231',
    model_year: new Date().getFullYear() + 1,
  }),
  actions: {
    setCountry(newCountry) {
        if (newCountry === 'Germany') {
          this.country = '231';
        }
        this.country = newCountry;
      },
    setModelYear(newModelYear) {
    this.model_year = newModelYear;
    },
    async fetchModels() {
        let path = `/db/${this.country}/${this.model_year}/models`
        return await index.get(path).then((response) => {
            this.models = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    async fetchEngines() {
        let path = `/db/${this.country}/${this.model_year}/engines`
        return await index.get(path).then((response) => {
            this.engines = response.data
        }).catch((error) => {
            console.log(error)
        })
        },
    async fetchSalesversions() {
        let path = `/db/${this.country}/${this.model_year}/sales_versions`
        return await index.get(path).then((response) => {
            this.salesversions = response.data
        }).catch((error) => {
            console.log(error)
        })
    },
    async fetchGearboxes() {
        let path = `/db/${this.country}/${this.model_year}/gearboxes`
        return await index.get(path).then((response) => {
            this.gearboxes = response.data
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
