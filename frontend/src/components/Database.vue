<template>
    <aside class="sidebar">
      <font size="6">PNO</font><br><br>

      <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option disabled value="0">Please Select...</option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>

    <br><br>
      <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>

    <br><br>
      <label class="engine" style="width: 180px;">Engine</label><br>
    <select name="engine" id="engine" v-model="engine" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="engine in engines" :key="engine" :value="engine">{{ engine }}</option>
    </select>

    <br><br>
      <label class="salesversion" style="width: 180px;">Sales Version</label><br>
    <select name="salesversion" id="salesversion" v-model="salesversion" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="salesversion in salesversions" :key="salesversion" :value="salesversion">{{ salesversion }}</option>
    </select>

    <br><br>
      <label class="gearbox" style="width: 180px;">Gearbox</label><br>
    <select name="gearbox" id="gearbox" v-model="gearbox" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="gearbox in gearboxes" :key="gearbox" :value="gearbox">{{ gearbox }}</option>
    </select>

    <br><br>
      <label class="displaytable" style="width: 180px;">Display Table</label><br>
      <select name="displaytable" v-model="displaytable" id="displaytable" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);" :disabled="this.pnoStore.model_year === '0'" @change="fetchPnosSpecifics($event.target.value)">
        <option disabled value="">Please Select...</option>
        <option value="Model">Model</option>       
        <option value="Engine">Engine</option>
        <option value="SalesVersion">Sales Version</option> 
        <option value="Features">Features</option>
        <option value="Colors">Colors</option>
        <option value="Options">Options</option>
        <option value="Upholstery">Upholstery</option>
      </select>

    <br><br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" @click="reset">Reset Filters</button>
    <br><br>
    <hr class ="divider">

    <font size="5">Manage Sources</font><br><br>

    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" onclick="document.getElementById('getFile').click()">Upload VISA file</button>
    <input type='file' class="visaupload" id="getFile" ref="file" style="display:none" accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" v-on:change="uploadVisa">
    <br><br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" @click="refreshCPAM">Refresh CPAM data</button>

    </aside>
    <main class="main-content">
  <!-- Model Table -->
  <table v-if="displaytable === 'Model'">
    <thead>
      <tr>
        <th>Model</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableModels" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Model }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.CPAMText }}</td>
        <td>
          <input type="MarketText" v-model="pno.MarketText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <button  class="action-button" v-if="pno.edited" @click="pushUpdateModel(pno)">Update</button>
          <button  class="action-button" v-if="pno.edited" @click="revert(pno)">Revert</button>
        </td>
      </tr>
    </tbody>
  </table>
  <!-- Salesversion Table -->
  <table v-if="displaytable === 'SalesVersion'">
    <thead>
      <tr>
        <th>Sales Version</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableSalesversions" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.SalesVersion }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.CPAMText }}</td>
        <td>
          <input type="MarketText" v-model="pno.MarketText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <button  class="action-button" v-if="pno.edited" @click="pushUpdateSV(pno)">Update</button>
          <button  class="action-button" v-if="pno.edited" @click="revert(pno)">Revert</button>
        </td>
      </tr>
    </tbody>
  </table>
    <!-- Engine Table -->
    <table v-if="displaytable === 'Engine'">
    <thead>
      <tr>
        <th>Engine</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th>Category</th>
        <th>Sub-Category</th>
        <th>Performance in kW (PS)</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableEngines" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Engine }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.CPAMText }}</td>
        <td>
          <input type="MarketText" v-model="pno.MarketText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="text" v-model="pno.Category" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="text" v-model="pno.Subcategory" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="Performance" v-model="pno.Performance" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td style="min-width: 140px;">
        <button class="action-button" v-show="pno.edited" @click="pushUpdateEngine(pno)">Update</button>
        <button class="action-button" v-show="pno.edited" @click="revert(pno)">Revert</button>
      </td>
      </tr>
    </tbody>
  </table>
  <!-- Features Table -->
  <table v-if="displaytable === 'Features'">
    <thead>
      <tr>
        <th>Feature</th>
        <th v-if="model === ''">Model</th>
        <th v-if="engine === ''">Engine</th>
        <th v-if="salesversion === ''">Sales Version</th>
        <th v-if="gearbox === ''">Gearbox</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in PnosSpecifics" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td v-if="model === ''" style="background-color: #f4f4f4;">{{ pno.Model }}</td>
        <td v-if="engine === ''" style="background-color: #f4f4f4;">{{ pno.Engine }}</td>
        <td v-if="salesversion === ''" style="background-color: #f4f4f4;">{{ pno.SalesVersion }}</td>
        <td v-if="gearbox === ''" style="background-color: #f4f4f4;">{{ pno.Gearbox }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.CPAMText }}</td>
        <td>
          <input type="MarketText" v-model="pno.MarketText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="text" v-model="pno.Category" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="text" v-model="pno.Subcategory" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td>
          <input type="Performance" v-model="pno.Performance" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
        <td style="min-width: 140px;">
          <button class="action-button" v-show="pno.edited" @click="pushUpdateEngine(pno)">Update</button>
          <button class="action-button" v-show="pno.edited" @click="revert(pno)">Revert</button>
        </td>
      </tr>
    </tbody>
  </table>
</main>

  </template>

  <script>
  import { usePNOStore } from '../stores/pno.js'
  import index from '../api/index.js'

  export default {
    name: 'DatabaseView',
    data() {
      return {
        model: '',
        model_year: '0',
        engine: '',
        salesversion: '',
        gearbox: '',
        displaytable: '',
        pnoStore: usePNOStore(),
      }
    },
    async created() {
      this.pnoStore.model_year = '0';
    },
    computed: {
      filteredPnos() {
        return this.pnoStore.filteredPnos(this.model, this.engine, this.salesversion, this.gearbox)
      },
      models() {
        return this.pnoStore.filteredModels(this.engine, this.salesversion, this.gearbox)
      },
      engines() {
        return this.pnoStore.filteredEngines(this.model, this.salesversion, this.gearbox)
      },
      salesversions() {
        return this.pnoStore.filteredSalesversions(this.model, this.engine, this.gearbox)
      },
      gearboxes() {
        return this.pnoStore.filteredGearboxes(this.model, this.engine, this.salesversion)
      },
      model_years() {
        return this.pnoStore.available_model_years
      },

      // Unique values for tables
      tableModels() {
        const unique = {};
        return this.tableFilteredPnos().filter(pno => {
          if (unique[pno.Model]) {
            return false;
          }
          unique[pno.Model] = true;
          return true;
        });
      },
      tableSalesversions() {
        const unique = {};
        return this.tableFilteredPnos().filter(pno => {
          if (unique[pno.SalesVersion]) {
            return false;
          }
          unique[pno.SalesVersion] = true;
          return true;
        });
      },
      tableEngines() {
        const unique = {};
        return this.tableFilteredPnos().filter(pno => {
          if (unique[pno.Engine]) {
            return false;
          }
          unique[pno.Engine] = true;
          return true;
        });
      },
      PnosSpecifics() {
        switch (this.type) {
          case 'Features':
            return this.pnoStore.pnosFeatures;
          case 'Color':
            return this.pnoStore.pnosColors;
          case 'Options':
            return this.pnoStore.pnosOptions;
          case 'Upholstery':
            return this.pnoStore.pnosUpholstery;
          default:
            console.log('Invalid type');
            return [];
        }
      },
    },
  methods: {

    tableFilteredPnos() {
        return this.pnoStore.filteredPnos(this.model, this.engine, this.salesversion, this.gearbox)
      },

    async fetchPnosSpecifics(type) {
      if (type === "Model" || type === "Engine" || type === "SalesVersion") {
        console.log(type + "Nope");
        return;
      } 
      await this.pnoStore.fetchPnosSpecifics(type, this.model, this.engine, this.salesversion, this.engine);
    },

    refreshModelyear() {
      this.pnoStore.model_year = this.model_year
      console.log('Model year refreshed')

      this.model = '';
      this.engine = '';
      this.salesversion = '';
      this.gearbox = '';
      this.displaytable = '';

      this.pnoStore.fetchPnos().then(() => {
      console.log('PNOs fetched')
    }).catch((error) => {
      console.error('Error fetching PNOs', error)
    })
    },

    reset() {
    this.model_year = '0';
    this.model = '';
    this.engine = '';
    this.salesversion = '';
    this.gearbox = '';
    this.displaytable = '';
    this.pnoStore.model_year = '0';

    this.pnoStore.fetchPnos().then(() => {
      console.log('PNOs fetched')
    }).catch((error) => {
      console.error('Error fetching PNOs', error)
    })
    },
    // Non-PNO-specific updates
    pushUpdateModel(pno) {
      this.pnoStore.pushUpdateModel(pno.Model, pno.MarketText)
      pno.edited = false
    },
    pushUpdateEngine(pno) {
      this.pnoStore.pushUpdateEngine(pno.Engine, pno.Category, pno.Subcategory, pno.Performance, pno.MarketText)
      pno.edited = false
    },
    pushUpdateSV(pno) {
      this.pnoStore.pushUpdateSV(pno.SalesVersion, pno.MarketText)
      pno.edited = false
    },
    revert(pno) {
      if (pno.originalMarketText) {
        pno.MarketText = pno.originalMarketText;
      }
      pno.edited = false;
    },
    startEditing(pno) {
      pno.originalMarketText = pno.MarketText;
    },
    uploadVisa() {
      const file = this.$refs.file.files[0];
      console.log(file)
      const formData = new FormData();
      formData.append('visa', file);
      index.post('/ingest/visa/upload', formData);
    },
    refreshCPAM() {
      index.get('/ingest/cpam');
    },
  }
  };

  </script>
  
  <style scoped>


  .main-content {
    padding: 2rem;
    height: 100vh;
    flex-grow: 1;
    overflow: auto;
  }

  .sidebar {
    width: 15.625rem;
    background-color: #f4f4f4;
    padding: 1rem;
    min-height: 1030px;
    position:relative;
    border-right: 1px solid #c8c9c7;
  }

  th {
  width: 180px;

  }

  .CPAMColumn {
  width: 200px; /* adjust as needed */
  }

  .editing {
    border: 2px solid black;
  }
  
  .action-button {
  margin-right: 5px; /* adjust as needed */
  }

  .model, .modelyear, .engine, .salesversion, .gearbox, .displaytable {
    text-align: left;
    display: inline-block;
    width:180px;
  }

  hr.divider {
  margin-top: 50px;
  border-top: 1px solid #c8c9c7;
  }

  /* @media (max-width: 1024px) {
    .sidebar {
    display: none;
    }
  } */

  </style>