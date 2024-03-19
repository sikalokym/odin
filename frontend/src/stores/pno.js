import { defineStore } from 'pinia'
import index from '../api/index.js'

export const usePNOStore = defineStore({
  id: 'pno',
  state: () => ({
    pnos: [],
    pnosFeatures: [],
    pnosColors: [],
    pnosOptions: [],
    pnosUpholstery: [],
    supported_countries: [],
    available_model_years: [],
    engine_cats: [],
    country: '231',
    model_year: new Date().getFullYear() + 1,
  }),
  getters: {
    models: (state) => [...new Set(state.pnos.map(vehicle => vehicle.Model))],
    engines: (state) => [...new Set(state.pnos.map(vehicle => vehicle.Engine))],
    salesversions: (state) => [...new Set(state.pnos.map(vehicle => vehicle.Salesversion))],
    gearboxes: (state) => [...new Set(state.pnos.map(vehicle => vehicle.Gearbox))],
    
    filteredPnos: (state) => (model, engine, salesversion, gearbox) => {
      return state.pnos.filter((pno) => {
        return (model === '' || pno.Model.includes(model)) &&
              (engine === '' || pno.Engine.includes(engine)) &&
              (salesversion === '' || pno.SalesVersion.includes(salesversion)) &&
              (gearbox === '' || pno.Gearbox.includes(gearbox))
      })
    },
    filteredModels: (state) => (engine, salesversion, gearbox) => {
      let validModels = state.pnos.filter((pno) => {
        return (engine === '' || pno.Engine.includes(engine)) &&
              (salesversion === '' || pno.SalesVersion.includes(salesversion)) &&
              (gearbox === '' || pno.Gearbox.includes(gearbox))
      })
      return [...new Set(validModels.map(vehicle => vehicle.Model))]
    },
    filteredEngines: (state) => (model, salesversion, gearbox) => {
      let validEngines = state.pnos.filter((pno) => {
        return (model === '' || pno.Model.includes(model)) &&
              (salesversion === '' || pno.SalesVersion.includes(salesversion)) &&
              (gearbox === '' || pno.Gearbox.includes(gearbox))
      })
      return [...new Set(validEngines.map(vehicle => vehicle.Engine))]
    },
    filteredSalesversions: (state) => (model, engine, gearbox) => {
      let validSalesversions = state.pnos.filter((pno) => {
        return (model === '' || pno.Model.includes(model)) &&
              (engine === '' || pno.Engine.includes(engine)) &&
              (gearbox === '' || pno.Gearbox.includes(gearbox))
      })
      return [...new Set(validSalesversions.map(vehicle => vehicle.SalesVersion))]
    },
    filteredGearboxes: (state) => (model, engine, salesversion) => {
      let validGearboxes = state.pnos.filter((pno) => {
        return (model === '' || pno.Model.includes(model)) &&
              (engine === '' || pno.Engine.includes(engine)) &&
              (salesversion === '' || pno.SalesVersion.includes(salesversion))
      })
      return [...new Set(validGearboxes.map(vehicle => vehicle.Gearbox))]
    }
  },
  actions: {
    async fetchSupportedCountries() {
      let path = `/setup/supported_countries`
      return await index.get(path).then((response) => {
        this.supported_countries = response.data
        console.log("Available countries fetched")
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchAvailableModelYears() {
      let path = `/setup/${this.country}/available_model_years`
      return await index.get(path).then((response) => {
        this.available_model_years = response.data
        console.log("Available model years fetched")
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchEngineCats(model) {
      let path = `/db/${this.country}/${this.model_year}/engine_cats?model=${model}`
      return await index.get(path).then((response) => {
        this.engine_cats = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnos() {
      let path = `/db/${this.country}/${this.model_year}/pnos`
      return await index.get(path).then((response) => {
        this.pnos = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosSpecifics(type, model, engine, salesversion, gearbox) {
      let path = `/db/${this.country}/${this.model_year}/pnosfeatures?type=${type}&model=${model}&engine=${engine}&salesversion=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        switch (type) {
          case 'Features':
            this.pnosFeatures = response.data;
            break;
          case 'Color':
            this.pnosColors = response.data;
            break;
          case 'Options':
            this.pnosOptions = response.data;
            break;
          case 'Upholstery':
            this.pnosUpholstery = response.data;
            break;
          default:
            console.log('Invalid type');
        }
      }).catch((error) => {
        console.log(error)
      })
    },
    setCountry(newCountry) {
      if (newCountry === 'Germany') {
        this.country = '231';
      }
      this.country = newCountry;
    },
    setModelYear(newModelYear) {
      this.model_year = newModelYear;
    },
    async exportVariantBinder(validity_year, validity_week, model, engine) {
      let path = `/${this.country}/export/variant_binder?yyyyuu=${validity_year}${validity_week}&model=${model}&engines_category=${engine}`;
      return await index.get(path, {responseType: 'blob'})
        .then((response) => {
          console.log(response);
          return response;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    async pushUpdateModel(model, translation) {
      const now = new Date();
      const year = now.getFullYear();
      const start = new Date(now.getFullYear(), 0, 1);
      const week = Math.ceil((((now - start) / 86400000) + start.getDay() + 1) / 7);
      const weekStr = week < 10 ? '0' + week : '' + week;
      const date = year + weekStr;
      let path = `/db/${this.country}/date=${date}&model=${model}&translation=${translation}`
      return index.post(path);
    },
    async pushUpdateEngine(engine, enginecategory, enginesubcategory, performance, translation) {
      const now = new Date();
      const year = now.getFullYear();
      const start = new Date(now.getFullYear(), 0, 1);
      const week = Math.ceil((((now - start) / 86400000) + start.getDay() + 1) / 7);
      const weekStr = week < 10 ? '0' + week : '' + week;
      const date = year + weekStr;
      let path = `/db/${this.country}/date=${date}&engine=${engine}&enginecategory=${enginecategory}&enginesubcategory=${enginesubcategory}&performance=${performance}&translation=${translation}`
      return index.post(path);
    },
    async pushUpdateSV(salesversion, translation) {
      const now = new Date();
      const year = now.getFullYear();
      const start = new Date(now.getFullYear(), 0, 1);
      const week = Math.ceil((((now - start) / 86400000) + start.getDay() + 1) / 7);
      const weekStr = week < 10 ? '0' + week : '' + week;
      const date = year + weekStr;
      let path = `/db/${this.country}/date=${date}&salesversion=${salesversion}&translation=${translation}`
      return index.post(path);
    },
  },
})