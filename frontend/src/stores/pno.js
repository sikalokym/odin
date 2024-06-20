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
    pnosPackages: [],
    pnosChangelog: [],
    supported_countries: [],
    available_model_years: [],
    engine_cats: [],
    country: '',
    model_year: new Date().getFullYear() + 1,
  }),
  getters: {
    models: (state) => [...new Set(state.pnos.map(vehicle => vehicle.Model))],
    customNames: (state) => [...new Set(state.pnos.map(vehicle => vehicle.CustomName))],
    modelCustomNameTuples: (state) => {
        const tuples = [];
        state.pnos.forEach(vehicle => {
            const tuple = [vehicle.Model, vehicle.CustomName];
            if (!tuples.some(t => t[0] === tuple[0] && t[1] === tuple[1])) {
                tuples.push(tuple);
            }
        });
        return tuples;
    },
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
    async fetchAvailableModelYears() {
      let path = `/setup/${this.country.Code}/available_model_years`
      return await index.get(path).then((response) => {
        this.available_model_years = response.data
        console.log("Available model years fetched")
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchEngineCats(model) {
      let path = `/db/${this.country.Code}/${this.model_year}/engine_cats?model=${model}`
      return await index.get(path).then((response) => {
        this.engine_cats = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnos() {
      let path = `/db/${this.country.Code}/${this.model_year}/pnos`
      return await index.get(path).then((response) => {
        this.pnos = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    // PNO specific
    async fetchPnosFeatures(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/features?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        this.pnosFeatures = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosOptions(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/options?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        this.pnosOptions = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosColors(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/colors?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        this.pnosColors = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosUpholstery(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/upholstery?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        this.pnosUpholstery = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosPackages(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/packages?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        this.pnosPackages = response.data
      }).catch((error) => {
        console.log(error)
      })
    },
    async fetchPnosChangelog(model, engine, salesversion, gearbox) {
      let path = `/db/${this.country.Code}/${this.model_year}/changelog?&model=${model}&engine=${engine}&sales_version=${salesversion}&gearbox=${gearbox}`
      return await index.get(path).then((response) => {
        response.data.forEach(item => {
          let date = new Date(item.ChangeDate);
          item.ChangeDate = date.toISOString().replace('T', ' ').substring(0, 19);
        });
        this.pnosChangelog = response.data;
      }).catch((error) => {
        console.log(error)
      })
    },
    // PNO-speficic updates
    async pushUpdateFeature(model, feature, translation, category, ID) {
      let updates = {
        Code: feature,
        CustomName: translation,
        CustomCategory: category
      }
      if (model !== '') {
        updates.Model = model;
      }
      let subpath = 'features';
      if (ID !== null && ID !== '') {
        updates.ID = ID;
        subpath = 'update/customfeatures';
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/${subpath}`
      return index.post(path, updates);
    },
    async pushNewCustomFeature(model, markettext, category, startDate, endDate) {
      let updates = {
        CustomName: markettext,
        CustomCategory: category,
        StartDate: startDate,
        EndDate: endDate
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/insert/customfeatures`
      return index.post(path, updates);
    },
    async deleteCustomFeature(model, ID) {
      let updates = {
        ID: ID,
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/delete/customfeatures`
      return index.post(path, updates);
    },
    async pushUpdateOption(model, option, translation) {
      let updates = {
        Code: option,
        CustomName: translation
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/options`
      return index.post(path, updates);
    },
    async pushUpdateColor(model, color, translation) {
      let updates = {
        Code: color,
        CustomName: translation
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/colors`
      return index.post(path, updates);
    },
    async pushUpdateUpholstery(model, upholstery, translation, customcategory) {
      let updates = {
        Code: upholstery,
        CustomName: translation,
        CustomCategory: customcategory
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/upholstery`
      return index.post(path, updates);
    },
    async pushUpdatePackage(model, packagecode, translation) {
      let updates = {
        Code: packagecode,
        CustomName: translation
      }
      if (model !== '') {
        updates.Model = model;
      }
      let path = `/db/${this.country.Code}/${this.model_year}/write/packages`
      return index.post(path, updates);
    },
    async setCountries(supported_countries) {
      this.supported_countries = supported_countries;
      this.country = supported_countries[0] || '';
    },
    async setCountry(newCountry) {
        this.country = newCountry;
    },
    setModelYear(newModelYear) {
      this.model_year = newModelYear;
    },
  },
})