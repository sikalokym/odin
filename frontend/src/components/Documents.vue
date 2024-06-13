reset<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">Specifications</span>
    <div style="margin-top: 10px;">
      <button v-on:click="setVariantBinderFilters" :class="{ 'highlighted': showFilters === 'VariantBinder' }">Variant
        Binder</button>
      <button v-on:click="setPricelistFilters" style="margin-left: 10px;"
        :class="{ 'highlighted': showFilters === 'Pricelist' }">SAP Pricelist
      </button>
    </div>
    <div v-if="showFilters === 'VariantBinder'">
      <!-- Filter for model years -->
      <label class="modelyear" style="width: 180px;">Model Year</label><br>
      <select name="model_year" id="model_year" v-model="model_year" @change="() => { refreshModelyear(); }"
        style="width:180px; height:30px; position: absolute;">
        <option disabled value="0">Please select Model Year...</option>
        <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
      </select>
      <!-- Filter for models -->
      <label class="model" style="width: 180px;">Model</label><br>
      <select name="model" id="model" v-model="model" @change="() => { refreshEnginecats(); getPnosVariantBinder(); }"
        style="width:180px; height:30px; position: absolute;">
        <option disabled value="">Please Select Model...</option>
        <option v-for="model in models.sort()" :key="model" :value="model">{{ model }}</option>
      </select>
      <!-- Filter for engine categories -->
      <label class="engine" style="width: 180px;">Engine Category</label><br>
      <select name="engine" id="engine" v-model="engine" @change="getPnosVariantBinder"
        style="width:180px; height:30px; position: absolute; margin-left: -90px;">
        <option disabled value="">Please Select Engine...</option>
        <option value="all">All</option>
        <option v-for="engine in engine_cats.sort()" :key="engine" :value="engine">{{ engine }}</option>
      </select>
      <br><br>
      <!-- Filter for validity date of the Variant Binder export -->
      <label class="validity_date" style="width: 180px;">Validity Date</label>
      <div class="validity"
        style="display: flex; gap: 10px; position:absolute; left: 50%; transform: translateX(-50%);">
        <select name="validity_year" id="validity_year" v-model="validity_year" @change="getPnosVariantBinder"
          style="width:85px; height:30px;">
          <option disabled value="">Year</option>
          <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year
            }}</option>
        </select>
        <select name="validity_week" id="validity_week" v-model="validity_week" @change="getPnosVariantBinder"
          style="width:85px; height:30px;">
          <option disabled value="">Week</option>
          <option v-for="n in validity_weeks" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0')
            }}</option>
        </select>
      </div>

      <!-- Export Variant Binder Button -->
      <button
        style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translateX(-50%); margin-top: 64px;"
        @click="exportVariantBinder"
        :disabled="exportInProgress || this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">
        Export Variant Binder
      </button>
    </div>
    <div v-else-if="showFilters === 'Pricelist'">
      <!-- Filter for model years -->
      <label class="modelyear" style="width: 180px;">Model Year</label><br>
      <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear"
        style="width:180px; height:30px; position: absolute;">
        <option disabled value="0">Please select Model Year...</option>
        <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
      </select>
      <!-- Filter for sales_channels -->
      <label class="sales_channel" style="width: 180px;">Sales Channel</label><br>
      <select name="sales_channel" id="sales_channel" v-model="sales_channel"
        style="width:180px; height:30px; position: absolute; margin-left: -90px; ">
        <option disabled value="">Select Sales Channel...</option>
        <option value="All">All</option>
        <option v-for="sales_channel in sales_channels" :key="sales_channel" :value="sales_channel.Code">{{
        sales_channel.Code }}</option>
      </select>
      <br><br>
      <!-- Filter for validity date of the Pricelsit export -->
      <label class="validity_date" style="width: 180px;">Validity Date</label>
      <div class="validity"
        style="display: flex; gap: 10px; position:absolute; left: 50%; transform: translateX(-50%);">
        <select name="validity_year" id="validity_year" v-model="validity_year" style="width:85px; height:30px;">
          <option disabled value="">Year</option>
          <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year
            }}</option>
        </select>
        <select name="validity_week" id="validity_week" v-model="validity_week" style="width:85px; height:30px;">
          <option disabled value="">Week</option>
          <option v-for="n in validity_weeks" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0')
            }}</option>
        </select>
      </div>
      <br><br><br>

      <!-- Export Pricelist Button -->
      <button
        style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translateX(-50%); margin-top: 24px;"
        @click="exportPricelist"
        :disabled="exportInProgress || this.pnoStore.model_year === '0' || this.sales_channel === ''">Export
        Pricelist</button>
    </div>
    <!-- Country Select Dropdown Menu -->
    <div class="bottom-div">
      <label for="country" class="countrylabel">Change Country: </label>
      <select v-model="selectedCountry" @change="changeCountry(this.selectedCountry)">
        <option v-for="country in supported_countries" :key="country" :value="country">{{ country.CountryName }}
        </option>
      </select>
    </div>
  </aside>
  <main class="main-content">
    <!-- PNOs Variant Binder Table -->
    <table v-if="variantBinderPnos.length > 0">
      <thead>
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Model
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Model', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Model', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Engine
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Engine', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Engine', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Sales Version
              <div style="margin-left: 1ch;">
                <span @click="sortTable('SalesVersion', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('SalesVersion', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Gearbox
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Gearbox', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Gearbox', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">In Export</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in variantBinderPnos" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">
            {{ '[' + pno.Model + '] ' + pno.CustomName }}
          </td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.Engine }}
          </td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.SalesVersion }}
          </td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.Gearbox }}
          </td>
          <td style="background-color: #f4f4f4;">
            <input type="checkbox" v-model="pno.InExport" />
          </td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<script>
import { usePNOStore } from '../stores/pno.js'
import { useEntitiesStore } from '../stores/entities.js'
import axios from '../api/index.js'

export default {
  name: 'DocumentsView',
  data() {
    return {
      model: '',
      model_year: '0',
      validity_year: '',
      validity_week: '',
      engine: '',
      variantBinderPnos: [],
      sales_channel: '',
      showFilters: 'VariantBinder',
      exportInProgress: false,
      pnoStore: usePNOStore(),
      entitiesStore: useEntitiesStore(),
      countries: [],
      selectedCountry: '',
    }
  },
  async created() {
    this.pnoStore.setModelYear('0');
    this.entitiesStore.setModelYear('0');
    this.selectedCountry = this.pnoStore.country;
    this.variantBinderPnos = [];
  },
  computed: {
    filteredPnos() {
      return this.pnoStore.filteredPnos(this.model, '0', '0', '0')
    },
    models() {
      return this.pnoStore.models
    },
    engine_cats() {
      return this.pnoStore.engine_cats
    },
    model_years() {
      return this.pnoStore.available_model_years
    },
    supported_countries() {
      return this.pnoStore.supported_countries
    },
    validity_years() {
      if (this.model_year === '0') {
        return;
      }
      return [this.model_year - 1, this.model_year];
    },
    validity_weeks() {
      if (this.validity_year == this.model_year) {
        return Array.from({ length: 16 }, (_, i) => i + 1);
      } else if (this.validity_year == this.model_year - 1) {
        return Array.from({ length: 36 }, (_, i) => i + 17);
      } else {
        return [];
      }
    },
    variantBinderPnosExport() {
      return this.variantBinderPnos
        .filter(pno => pno.InExport)
        .map(pno => pno.ID)
        .join(',');
    },
    canExport() {
      return !this.exportInProgress && this.model_year !== '0' && this.model !== '' && this.validity_year !== '' && this.validity_week !== '';
    },
    sales_channels() {
      return this.entitiesStore.saleschannels
    },
    bottomDivStyle() {
      if (this.showFilters === '') {
        return { marginTop: '837px' };
      } else {
        return { marginTop: '585px' };
      }
    },
  },
  methods: {
    setVariantBinderFilters() {
      this.showFilters = 'VariantBinder';
      this.model = '';
      this.model_year = '0';
      this.validity_year = '';
      this.validity_week = '';
      this.engine = '';
      this.variantBinderPnos = [];
      this.sales_channel = '';
    },
    setPricelistFilters() {
      this.showFilters = 'Pricelist';
      this.model = '';
      this.model_year = '0';
      this.validity_year = '';
      this.validity_week = '';
      this.engine = '';
      this.variantBinderPnos = [];
      this.sales_channel = '';
    },
    async refreshModelyear() {
      this.pnoStore.setModelYear(this.model_year)
      this.entitiesStore.setModelYear(this.model_year);
      console.log('Model year refreshed')

      if (this.showFilters === 'VariantBinder') {
        await this.pnoStore.fetchPnos()
      } else if (this.showFilters === 'Pricelist') {
        await this.entitiesStore.fetchSalesChannels().then(() => {
          console.log('Sales channels fetched')
        }).catch((error) => {
          console.error('Error fetching sales channels', error)
        })
      }
      this.model = '';
      this.engine = '';
      this.validity_year = '';
      this.validity_week = '';
    },
    refreshEnginecats() {
      this.pnoStore.fetchEngineCats(this.model)
      console.log('Engine cats refreshed')
    },
    async getPnosVariantBinder() {
      if (this.model_year == '0' || this.model == '' || this.validity_year == '' || this.validity_week == '') {
        return;
      }
      let path = `/${this.selectedCountry.Code}/export/variant_binder/pnos?date=${this.validity_year}${this.validity_week}&model=${this.model}&engines_category=${this.engine}`;
      return await axios.get(path).then((response) => {
        this.variantBinderPnos = response.data.map(pno => ({
          ...pno,
          InExport: true
        }));
      }).catch((error) => {
        console.log(error)
      })
    },
    async exportVariantBinder() {
      this.exportInProgress = true;
      const link = document.createElement('a');
      let link_href = `${axios.endpoint}/${this.selectedCountry.Code}/export/variant_binder?date=${this.validity_year}${this.validity_week}&model=${this.model}&engines_category=${this.engine}&pnos=${this.variantBinderPnosExport}`;
      link_href = encodeURI(link_href);
      link.href = link_href;

      link.setAttribute('download', 'VariantBinder_.xlsx');
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        this.exportInProgress = false;
      }, 10000);
    },
    async exportPricelist() {
      this.exportInProgress = true;
      const link = document.createElement('a');
      link.href = `${axios.endpoint}/${this.selectedCountry.Code}/export/sap-price-list?date=${this.validity_year}${this.validity_week}&code=${this.sales_channel}`;
      console.log(link.href);
      link.setAttribute('download', 'SAP_Price_Lists.zip');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(() => {
        this.exportInProgress = false;
      }, 10000);
    },
    async changeCountry(newCountry) {
      await this.pnoStore.setCountry(newCountry);
      await this.entitiesStore.setCountry(newCountry);
    },
  }
};

</script>

<style scoped>
.validity {
  display: flex;
  gap: 10px;
}

.main-content {
  z-index: 1;
  position: relative;
  margin-left: 312px;
  padding: 2rem;
  flex-grow: 1;
  overflow: auto;
  height: calc(100vh - 4rem - 100px);
  /* Adjust as needed */
}

td {
  min-width: 180px;
}

th {
  min-width: 180px;
}

.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 1rem;
  position: fixed;
  top: 82px;
  bottom: 0;
  overflow-y: auto;
  border-right: 1px solid #c8c9c7;
}

.title {
  display: block;
  /* margin-bottom: -20px; */
}

.modelyear {
  text-align: left;
  display: inline-block;
  width: 180px;
  margin-top: 28px;
}

.model,
.engine,
.sales_channel {
  text-align: left;
  display: inline-block;
  width: 180px;
  margin-top: 42px;
}

.validity_date {
  margin-left: -91px;
}

.countrylabel {
  margin-right: 10px;
}

.bottom-div {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 10px;
  display: flex;
  align-items: center;
}

.highlighted {
  background-color: #f0f0f0;
}
</style>