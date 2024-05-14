<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">Reports</span>
    <!-- Table Selection -->
    <label class="displaytable" style="width: 180px;">Report Type</label><br>
    <select name="displaytable" v-model="displaytable" id="displaytable" @change="fetchPnoSpecifics(); displaytablereset()" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select...</option>
      <option value="Changelog">Changelog</option>       
    </select>
    <!-- Filter for model years -->
    <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear(); fetchPnoSpecifics()" style="width:180px; height:30px; position: absolute;" :disabled="displaytable === ''">
      <option disabled value="0">Please Select...</option>
      <option value="0000" :disabled="!['Model', 'Engine', 'SalesVersion', 'Gearbox'].includes(displaytable)">All</option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>
    <!-- Filter for models -->
    <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model" @change="fetchPnoSpecifics" style="width:180px; height:30px; position: absolute;" :disabled="!['Changelog'].includes(displaytable) || model_year === '0'">
      <option value="" :disabled="!['Changelog'].includes(displaytable)">All</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>

    <!-- Filter Reset Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top: 64px;" @click="reset">Reset Filters</button>
  </aside>
  <main class="main-content">
    <!-- Changelog Table -->
    <table v-if="displaytable === 'Changelog' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Table</th>
          <th>Type</th>
          <th>Field</th>
          <th>From</th>
          <th>To</th>
          <th>Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableChangelog" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td class="ChangeTable" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeTable}}</td>
          <td class="ChangeType" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeType}}</td>
          <td class="ChangeField" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeField}}</td>
          <td class="ChangeFrom" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeFrom}}</td>
          <td class="ChangeTo" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeTo}}</td>
          <td class="ChangeDate" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeDate}}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>



<script>
import { usePNOStore } from '../stores/pno.js'
import { useEntitiesStore } from '../stores/entities.js'
import index from '../api/index.js'

export default {
  name: 'ReportsView',
  data() {
    return {
      model: '',
      model_year: '0',
      engine: '',
      salesversion: '',
      gearbox: '',
      displaytable: '',
      pnoStore: usePNOStore(),
      entitiesStore: useEntitiesStore(),
      countries: useEntitiesStore().countries,
      selectedCountry: '231',
    }
  },
  async created() {
    this.pnoStore.setModelYear('0');
    this.entitiesStore.setModelYear('0');
  },
  computed: {
    filteredPnos() {
      return this.pnoStore.filteredPnos(this.model, this.engine, this.salesversion, this.gearbox)
    },
    models() {
      return this.pnoStore.filteredModels(this.engine, this.salesversion, this.gearbox)
    },
    model_years() {
      return this.pnoStore.available_model_years
    },
    countries() {
      return this.pnoStore.supported_countries
    },
    // Unique values for tables
    tableChangelog() {
      return this.pnoStore.pnosChangelog
    },
  },
methods: {

  async refreshModelyear() {
    await this.pnoStore.setModelYear(this.model_year)
    await this.entitiesStore.setModelYear(this.model_year)
    console.log(this.model_year)
    console.log('Model year refreshed')

    this.model = '';
    this.engine = '';
    this.salesversion = '';
    this.gearbox = '';

    await this.fetchEntities();

    await this.pnoStore.fetchPnos().then(() => {
    console.log('PNOs fetched')
    }).catch((error) => {
      console.error('Error fetching PNOs', error)
    })
  },

  async fetchEntities() {
    try {
      if (this.displaytable === 'Changelog') {
      await this.entitiesStore.fetchModels();
      console.log('Model text fetched');
      }
    } catch (error) {
      console.error('Error fetching data', error);
    }
  },

  async fetchPnoSpecifics() {
    try {
      if (this.displaytable === 'Changelog') {
        await this.pnoStore.fetchPnosChangelog(this.model, this.engine, this.salesversion, this.gearbox);
        console.log('PNO Changelog fetched');
      }
    } catch (error) {
      console.error('Error fetching data', error);
    }
  },

  async reset() {
    this.model_year = '0';
    this.model = '';
    this.engine = '';
    this.salesversion = '';
    this.gearbox = '';
    this.displaytable = '';
    this.customFeatureTable = false;
    await this.pnoStore.setModelYear('0');
  },
  async displaytablereset() {
    this.model_year = '0';
    this.model = '';
    await this.pnoStore.setModelYear('0');
  },
}
};

</script>
  
<style scoped>


.main-content {
  margin-left: 312px;
  padding: 2rem;
  flex-grow: 1;
  overflow: auto;
  height: calc(100vh - 4rem - 100px); /* Adjust as needed */
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

td {
min-width: 180px;

}

.editing {
  border: 2px solid black;
}

.title {
  display: block;
  margin-bottom: -20px;
}

.model, .modelyear, .displaytable {
  text-align: left;
  display: inline-block;
  width:180px;
  margin-top: 42px;
}

hr.divider {
  margin-top: 50px;
  border-top: 1px solid #c8c9c7;
}

.countrylabel {
  margin-right: 10px;
} 
.bottom-div {
  margin-top: 128px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>