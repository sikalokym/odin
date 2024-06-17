import { defineStore } from 'pinia'
import index from '../api/index.js'

export const useEntitiesStore = defineStore({
    id: 'entities',
    state: () => ({
        models: [],
        engines: [],
        salesversions: [],
        gearboxes: [],
        supported_countries: [],
        visafiles: [],
        visafile: [],
        discounts: [],
        customlocaloptions: [],
        saleschannels: [],
        country: '',
        model_year: new Date().getFullYear() + 1,
    }),
    actions: {
        async setCountry(newCountry) {
            this.country = newCountry;
        },
        setModelYear(newModelYear) {
            this.model_year = newModelYear;
        },
        async fetchSupportedCountries(user_allowed_countries) {
            let path = `/setup/supported_countries`
            return index.get(path).then((response) => {
                let all_countries = response.data
                console.log('User allowed countries', all_countries)
                this.supported_countries = all_countries.filter(country => user_allowed_countries.includes(country.CountryName.toLowerCase()))
                this.country = this.supported_countries[0] || ''
                return this.supported_countries
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchModels() {
            let path = `/db/${this.country.Code}/${this.model_year}/models`
            return await index.get(path).then((response) => {
                this.models = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchEngines() {
            let path = `/db/${this.country.Code}/${this.model_year}/engines`
            return await index.get(path).then((response) => {
                this.engines = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchSalesversions() {
            let path = `/db/${this.country.Code}/${this.model_year}/sales_versions`
            return await index.get(path).then((response) => {
                this.salesversions = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchGearboxes() {
            let path = `/db/${this.country.Code}/${this.model_year}/gearboxes`
            return await index.get(path).then((response) => {
                this.gearboxes = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchVISAFiles() {
            let path = `/db/${this.country.Code}/${this.model_year}/visa-files`
            return await index.get(path).then((response) => {
                this.visafiles = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchVISAFile(visafile) {
            //Visa File contains spaces, so we need to encode it.
            visafile = encodeURIComponent(visafile)
            let path = `/db/${this.country.Code}/${this.model_year}/visa-file?&VisaFile=${visafile}`
            return await index.get(path).then((response) => {
                this.visafile = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchSalesChannels() {
            let path = `/db/${this.country.Code}/${this.model_year}/sales-channels`
            return await index.get(path).then((response) => {
                this.saleschannels = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchDiscounts(id) {
            let path = `/db/${this.country.Code}/${this.model_year}/discounts?&id=${id}`
            return await index.get(path).then((response) => {
                this.discounts = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchCustomLocalOptions(id) {
            let path = `/db/${this.country.Code}/${this.model_year}/custom-local-options?&id=${id}`
            return await index.get(path).then((response) => {
                this.customlocaloptions = response.data
            }).catch((error) => {
                console.log(error)
            })
        },
        async fetchCountries() {
            let path = `/setup/supported_countries`
            return await index.get(path).then((response) => {
                this.supported_countries = response.data
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
            let path = `/db/${this.country.Code}/${this.model_year}/write/models`
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
            let path = `/db/${this.country.Code}/${this.model_year}/write/engines`
            return index.post(path, updates);
        },
        async pushUpdateSV(salesversion, translation) {
            let updates = {
                Code: salesversion,
                CustomName: translation,
            }
            let path = `/db/${this.country.Code}/${this.model_year}/write/sales_versions`
            return index.post(path, updates);
        },
        async pushUpdateGearbox(gearbox, translation) {
            let updates = {
                Code: gearbox,
                CustomName: translation,
            }
            let path = `/db/${this.country.Code}/${this.model_year}/write/gearboxes`
            return index.post(path, updates);
        },
        async pushUpdateVISAFile(OldName, NewName) {
            let updates = {
                OldName: OldName,
                NewName: NewName,
            }
            console.log(OldName)
            console.log(NewName)
            let path = `/db/${this.country.Code}/${this.model_year}/write/visa/rename`
            return index.post(path, updates);
        },
        async pushUpdateVISAFileInformation(ID, Active, SalesOrg, DistrCh, PriceList, DealerGroup, Country, CarType, Engine, SalesVersion, Body, Gearbox, Steering, MarketCode, ModelYear, StructureWeek, DateFrom, DateTo, Currency, Color, Options, Upholstery, Package, SNote, MSRP, TAX2, VAT, TAX1, PriceBeforeTax, WholesalePrice, TransferPrice, VisaFile, CountryCode, LoadingDate) {
            let updates = {
                Active: Active,
                SalesOrg: SalesOrg,
                DistrCh: DistrCh,
                PriceList: PriceList,
                DealerGroup: DealerGroup,
                Country: Country,
                CarType: CarType,
                Engine: Engine,
                SalesVersion: SalesVersion,
                Body: Body,
                Gearbox: Gearbox,
                Steering: Steering,
                MarketCode: MarketCode,
                ModelYear: ModelYear,
                StructureWeek: StructureWeek,
                DateFrom: DateFrom,
                DateTo: DateTo,
                Currency: Currency,
                Color: Color,
                Options: Options,
                Upholstery: Upholstery,
                Package: Package,
                SNote: SNote,
                MSRP: MSRP,
                TAX2: TAX2,
                VAT: VAT,
                TAX1: TAX1,
                PriceBeforeTax: PriceBeforeTax,
                WholesalePrice: WholesalePrice,
                TransferPrice: TransferPrice,
                VisaFile: VisaFile,
                CountryCode: CountryCode,
                LoadingDate: LoadingDate
            }
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country.Code}/${this.model_year}/write/visa`
            return index.post(path, updates);
        },
        async deleteVISAFileInformation(ID) {
            let path = `/db/${this.country.Code}/${this.model_year}/write/visa/data?ID=${ID}`
            return index.delete(path);
        },
        async pushUpdateSalesChannel(ID, Code, ChannelName, Comment, DateFrom, DateTo) {
            let updates = {
                Code: Code,
                ChannelName: ChannelName,
                Comment: Comment,
                DateFrom: DateFrom,
                DateTo: DateTo
            };
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country.Code}/${this.model_year}/write/sales-channels`
            return index.post(path, updates);
        },
        async deleteSalesChannel(ID) {
            let path = `/db/${this.country.Code}/${this.model_year}/write/sales-channels?ID=${ID}`
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
            let path = `/db/${this.country.Code}/${this.model_year}/write/discounts`
            return index.post(path, updates);
        },
        async deleteDiscount(ID) {
            let path = `/db/${this.country.Code}/${this.model_year}/write/discounts?ID=${ID}`
            return index.delete(path);
        },
        async pushUpdateCustomLocalOptions(ID, SalesChannelID, FeatureCode, FeatureRetailPrice, FeatureWholesalePrice, AffectedVisaFile, DateFrom, DateTo) {
            let updates = {
                ChannelID: SalesChannelID,
                FeatureCode: FeatureCode,
                FeatureRetailPrice: FeatureRetailPrice,
                FeatureWholesalePrice: FeatureWholesalePrice,
                AffectedVisaFile: AffectedVisaFile,
                DateFrom: DateFrom,
                DateTo: DateTo
            }
            if (ID !== null) {
                updates.ID = ID;
            }
            let path = `/db/${this.country.Code}/${this.model_year}/write/custom-local-options`
            return index.post(path, updates);
        },
        async deleteCustomLocalOptions(ID) {
            let path = `/db/${this.country.Code}/${this.model_year}/write/custom-local-options?ID=${ID}`
            return index.delete(path);
        },
        async deleteVISAFile(file_name) {
            let path = `/db/${this.country.Code}/${this.model_year}/write/visa?VisaFile=${file_name}`
            return index.delete(path);
        },
    },
})
