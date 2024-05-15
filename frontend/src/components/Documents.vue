<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">Specifications</span>
    <div style="margin-top: 10px;">
    <button 
      v-on:click="showFilters = 'VariantBinder'; console.log(showFilters)" 
      :class="{ 'highlighted': showFilters === 'VariantBinder' }">Variant Binder</button>
    <button 
      v-on:click="showFilters = 'Pricelist'; console.log(showFilters)" 
      style="margin-left: 10px;" 
      :class="{ 'highlighted': showFilters === 'Pricelist' }">Pricelist
    </button>
  </div>
  <div v-if="showFilters === 'VariantBinder'">
    <!-- Filter for model years -->
    <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear" style="width:180px; height:30px; position: absolute;">
      <option disabled value="0">Please select Model Year...</option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>
    <!-- Filter for models -->
    <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model"  @change="refreshEnginecats" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select Model...</option>
      <option v-for="model in models.sort()" :key="model" :value="model">{{ model }}</option>
    </select>
    <!-- Filter for engine categories -->
    <label class="engine" style="width: 180px;">Engine Category</label><br>
    <select name="engine" id="engine" v-model="engine" style="width:180px; height:30px; position: absolute; margin-left: -90px;">
      <option disabled value="">Please Select Engine...</option>
      <option value="all">All</option>
      <option v-for="engine in engine_cats.sort()" :key="engine" :value="engine">{{ engine }}</option>
    </select>
    <br><br>
    <!-- Filter for validity date of the Variant Binder export -->
    <label class="validity_date" style="width: 180px;">Validity Date</label>
    <div class="validity" style="display: flex; gap: 10px; position:absolute; left: 50%; transform: translateX(-50%);">
      <select name="validity_year" id="validity_year" v-model="validity_year" style="width:85px; height:30px;">
        <option disabled value="">Year</option>
        <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year }}</option>
      </select>
      <select name="validity_week" id="validity_week" v-model="validity_week" style="width:85px; height:30px;">
        <option disabled value="">Week</option>
        <option v-for="n in validity_weeks" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0') }}</option>
      </select>
    </div>

    <!-- Export Variant Binder Button -->
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translateX(-50%); margin-top: 64px;" @click="exportVariantBinder" :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Variant Binder</button>
  </div>
  <div v-else-if="showFilters === 'Pricelist'">
    <!-- Filter for model years -->
    <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear" style="width:180px; height:30px; position: absolute;">
      <option disabled value="0">Please select Model Year...</option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>
    <!-- Filter for models -->
    <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model"  @change="refreshEnginecats" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select Model...</option>
      <option value="0">All</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>
    <!-- Filter for type of export -->
    <label class="engine" style="width: 180px;">Export Type</label><br>
    <select name="engine" id="engine" v-model="engine" style="width:180px; height:30px; position: absolute; margin-left: -90px;">
      <option disabled value="">Please Select Export...</option>
      <option value="all">Single File</option>
      <option value="model">Multiple Files</option>
    </select>
    <br><br>
    <!-- Filter for validity date of the Variant Binder export -->
    <label class="validity_date" style="width: 180px;">Validity Date</label>
    <div class="validity" style="display: flex; gap: 10px; position:absolute; left: 50%; transform: translateX(-50%);">
      <select name="validity_year" id="validity_year" v-model="validity_year" style="width:85px; height:30px;">
        <option disabled value="">Year</option>
        <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year }}</option>
      </select>
      <select name="validity_week" id="validity_week" v-model="validity_week" style="width:85px; height:30px;">
        <option disabled value="">Week</option>
        <option v-for="n in validity_weeks" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0') }}</option>
      </select>
    </div>

    <!-- Export Pricelist Button -->
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translateX(-50%); margin-top: 64px;" @click="exportPricelist" :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Pricelist</button>
  </div>
    <!-- Country Select Dropdown Menu -->
    <div class="bottom-div">
      <label for="country" class="countrylabel">Change Country: </label>
      <select v-model="selectedCountry" @change="changeCountry(this.selectedCountry)">
        <option value="231" selected disabled>Germany</option>
      </select>
    </div>
  </aside>
  <main class="main-content">
  <!-- At present, no content is displayed here -->
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
        showFilters: 'VariantBinder',
        pnoStore: usePNOStore(),
        entitiesStore: useEntitiesStore(),
        countries: [],
        selectedCountry: '231',
      }
  },
  async created() {
    this.pnoStore.setModelYear('0');
    this.entitiesStore.setModelYear('0');
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
    validity_years() {
      if (this.model_year === '0') {
        return;
      }
    return [this.model_year - 1, this.model_year];
    },
    validity_weeks() {
      if (this.validity_year == this.model_year) {
        return Array.from({length: 16}, (_, i) => i + 1);
      } else if (this.validity_year == this.model_year - 1) {
        return Array.from({length: 36}, (_, i) => i + 17);
      } else {
        return [];
      }
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
    refreshModelyear() {
      this.pnoStore.setModelYear(this.model_year)
      console.log('Model year refreshed')

      this.pnoStore.fetchPnos()
      this.model = '';
      this.engine = '';
      this.validity_year = '';
      this.validity_week = '';
    },
    refreshEnginecats() {
      this.pnoStore.fetchEngineCats(this.model)
      console.log('Engine cats refreshed')
    },
    async exportVariantBinder() {
      const link = document.createElement('a');
      link.href = `${axios.endpoint}/231/export/variant_binder?date=${this.validity_year}${this.validity_week}&model=${this.model}&engines_category=${this.engine}`;
      console.log(link.href);
      link.setAttribute('download', 'VariantBinder_.xlsx');
      document.body.appendChild(link);
      link.click();
    },
    changeCountry(newCountry) {
      this.pnoStore.setCountry(newCountry);
      this.entitiesStore.setCountry(newCountry);
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
  padding: 2rem;
  /* height: 100vh; */
  flex-grow: 1;
  overflow: auto;
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

.modelyear{
  text-align: left;
  display: inline-block;
  width:180px;
  margin-top: 28px;
}

.model, .engine {
  text-align: left;
  display: inline-block;
  width:180px;
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