<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">Specifications</span>
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
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>
    <!-- Filter for engine categories -->
    <label class="engine" style="width: 180px;">Engine Category</label><br>
    <select name="engine" id="engine" v-model="engine" style="width:180px; height:30px; position: absolute; margin-left: -90px;">
      <option disabled value="">Please Select Engine...</option>
      <option value="">All</option>
      <option v-for="engine in engine_cats" :key="engine" :value="engine">{{ engine }}</option>
    </select>
    <br><br>
    <!-- Filter for validity date of the Variant Binder export -->
    <label class="validity_date" style="width: 180px;">Validity Date</label>
    <div class="validity" style="display: flex; gap: 10px;">
      <select name="validity_year" id="validity_year" v-model="validity_year" style="width:85px; height:30px; ">
        <option disabled value="">Year</option>
        <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year }}</option>
      </select>
      <select name="validity_week" id="validity_week" v-model="validity_week" style="width:85px; height:30px;">
        <option disabled value="">Week</option>
        <option v-for="n in 53" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0') }}</option>
      </select>
    </div>

    <!-- Export Variant Binder Button -->
    <button style="display:block;width:180px; height:50px; margin-left: 35px; margin-top: 64px;" @click="exportVariantBinder" :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Variant Binder</button>
    <!-- Export Changelog Button --> 
    <button style="display:block;width:180px; height:50px; margin-left: 35px; margin-top: 10px;" :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Changelog</button>

    <!-- Country Select Dropdown Menu -->
    <div class="country bottom-div">
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

  export default {
    name: 'DocumentsView',
    data() {
      return {
        model: '',
        model_year: '0',
        validity_year: '',
        validity_week: '',
        engine: '',
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
    return [this.model_year - 1, this.model_year, this.model_year + 1];
    }
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
        // link.href = `https://pmt-portal-backend.azurewebsites.net/api/231/export/variant_binder?date=${this.validity_year}${this.validity_week}&model=${this.model}&engines_category=${this.engine}`;
        link.href = `http://127.0.0.1:5000/api/231/export/variant_binder?date=${this.validity_year}${this.validity_week}&model=${this.model}&engines_category=${this.engine}`;
  
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
  margin-top: -1px;
  margin-left: 35px;
  position: absolute; 
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
  margin-bottom: -20px;
}

.model, .modelyear, .engine {
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
  margin-top: 417px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>