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
        visafiles: [],
        discounts: [],
        customlocaloptions: [],
        saleschannels: [],
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
        async fetchVISAFiles() {
            let path = `/db/${this.country}/${this.model_year}/visa-files`
            return await index.get(path).then((response) => {
                this.visafiles = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchSalesChannels() {
            let path = `/db/${this.country}/${this.model_year}/sales-channels`
            return await index.get(path).then((response) => {
                this.saleschannels = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchDiscounts(id) {
            let path = `/db/${this.country}/${this.model_year}/discounts?&id=${id}`
            return await index.get(path).then((response) => {
                this.discounts = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchCustomLocalOptions(id) {
            let path = `/db/${this.country}/${this.model_year}/custom-local-options?&id=${id}`
            return await index.get(path).then((response) => {
                this.customlocaloptions = response.data
                console.log("Custom Local Options fetched: ")
                console.log(this.customlocaloptions)
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
                CustomName: translation,
            }
            let path = `/db/${this.country}/${this.model_year}/write/models`
            return index.post(path, updates);
        },
        async pushUpdateEngine(engine, translation, enginecategory, enginetype, performance) {
            let updates = {
                Code: engine,
                CustomName: translation,
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
                CustomName: translation,
            }
            let path = `/db/${this.country}/${this.model_year}/write/sales_versions`
            return index.post(path, updates);
        },
        async pushUpdateGearbox(gearbox, translation) {
            let updates = {
                Code: gearbox,
                CustomName: translation,
            }
            let path = `/db/${this.country}/${this.model_year}/write/gearboxes`
            return index.post(path, updates);
        },
        async pushUpdateSalesChannel(ID, Code, ChannelName, Comment, StartDate, EndDate) {
            let updates = {
                Code: Code,
                ChannelName: ChannelName,
                Comment: Comment,
                StartDate: StartDate,
                EndDate: EndDate
            };
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country}/${this.model_year}/write/sales-channels`
            return index.post(path, updates);
        },
        async deleteSalesChannel(ID) {
            let path = `/db/${this.country}/${this.model_year}/write/sales-channels?ID=${ID}`
            return index.delete(path);
        },
        async pushUpdateDiscount(ID, SalesChannelID, DiscountPercentage, RetailPrice, WholesalePrice, PNOSpecific, AffectedVisaFile) {
            let updates = {
                ChannelID: SalesChannelID,
                DiscountPercentage: DiscountPercentage,
                RetailPrice: RetailPrice,
                WholesalePrice: WholesalePrice,
                PNOSpecific: PNOSpecific,
                AffectedVisaFile: AffectedVisaFile
            }
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country}/${this.model_year}/write/discounts`
            return index.post(path, updates);
        },
        async deleteDiscount(ID) {
            let path = `/db/${this.country}/${this.model_year}/write/discounts?ID=${ID}`
            return index.delete(path);
        },
        async pushUpdateCustomLocalOptions(ID, SalesChannelID, FeatureCode, FeatureRetailPrice, FeatureWholesalePrice) {
            let updates = {
                ChannelID: SalesChannelID,
                FeatureCode: FeatureCode,
                FeatureRetailPrice: FeatureRetailPrice,
                FeatureWholesalePrice: FeatureWholesalePrice
            }
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country}/${this.model_year}/write/custom-local-options`
            return index.post(path, updates);
        },
        async deleteCustomLocalOptions(ID) {
            let path = `/db/${this.country}/${this.model_year}/write/custom-local-options?ID=${ID}`
            return index.delete(path);
        },
        async deleteVisaFile(file_name) {
            let updates = {
                file_name: file_name,
            }
            let path = `/db/${this.country}/${this.model_year}/write/visa_files`
            return index.post(path, updates);
        },
    },
})
