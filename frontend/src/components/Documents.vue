<template>
    <aside class="sidebar">
      <font size="6">Specifications</font><br><br>
      <label class="modelyear" style="width: 180px;">Model Year</label><br>
      <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear" style="width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
    <option disabled value="0">Year</option>
    <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
  </select>
  <br><br>
      <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model"  @change="refreshEnginecats" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option disabled value="">Please Select Model...</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>
    <br><br>

      <label class="engine" style="width: 180px;">Engine Category</label><br>
    <select name="engine" id="engine" v-model="engine" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option disabled value="">Please Select Engine...</option>
      <option v-for="engine in engine_cats" :key="engine" :value="engine">{{ engine }}</option>
    </select>
    <br><br>

    <label class="validity_date" style="width: 180px;">Validity Date</label><br>
      <div class="validity" style="display: flex; gap: 10px;">
  <select name="validity_year" id="validity_year" v-model="validity_year" style="width:85px; height:30px;">
    <option disabled value="">Year</option>
    <option v-for="validity_year in validity_years" :key="validity_year" :value="validity_year">{{ validity_year }}</option>
  </select>
  <select name="validity_week" id="validity_week" v-model="validity_week" style="width:85px; height:30px;">
  <option disabled value="">Week</option>
  <option v-for="n in 53" :key="n" :value="String(n).padStart(2, '0')">{{ String(n).padStart(2, '0') }}</option>
</select>
</div>

    <br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" @click="exportVariantBinder" :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Variant Binder</button>
    <br><br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%); " :disabled="this.pnoStore.model_year === '0' || this.model === '' || this.model === '' || this.validity_year === '' || this.validity_week === ''">Export Changelog</button>
    <br><br>
    </aside>
    <main class="main-content">

    </main>
  </template>
  
  <script>
  import { usePNOStore } from '../stores/pno.js'

  export default {
    name: 'DocumentsView',
    data() {
      return {
        model: '',
        model_year: '0',
        validity_year: '',
        validity_week: '',
        engine: '',
        pnoStore: usePNOStore()
      }
    },
    async created() {
      this.pnoStore.model_year = '0';
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
        this.pnoStore.model_year = this.model_year
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
        let response = await this.pnoStore.exportVariantBinder(this.validity_year,this.validity_week,this.model,this.engine)
        console.log(response)
        const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
    
          // Extract filename from download_name header
          let filename = response.headers['download_name']; // Default filename if download_name is not present
    
          link.setAttribute('download', filename);
          document.body.appendChild(link);
          link.click();
          console.log(response.headers)
      },
  
  }
  };

</script>

<style scoped>

.validity {
margin-left: 36px;
}

.main-content {
  padding: 2rem;
  margin-left: 250px;
}

.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 1rem;
  height: 100vh;
  position:fixed; 
  border-right: 1px solid #c8c9c7;
}

.model, .modelyear, .engine .validity_date {
  text-align: left;
  display: inline-block;
}

.validity_date {
  margin-left: -89px;
}
.engine {
  margin-left: -64px;
}
</style>