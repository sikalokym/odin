<template>
    <aside class="sidebar">
      <span style="font-size: 32px;">PNO</span><br><br>

      <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option disabled value="0">Please Select...</option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>

    <br><br>
      <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model" @change="fetchPnoSpecifics" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>

    <br><br>
      <label class="engine" style="width: 180px;">Engine</label><br>
    <select name="engine" id="engine" v-model="engine" @change="fetchPnoSpecifics" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="engine in engines" :key="engine" :value="engine">{{ engine }}</option>
    </select>

    <br><br>
      <label class="salesversion" style="width: 180px;">Sales Version</label><br>
    <select name="salesversion" id="salesversion" v-model="salesversion" @change="fetchPnoSpecifics" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="salesversion in salesversions" :key="salesversion" :value="salesversion">{{ salesversion }}</option>
    </select>

    <br><br>
      <label class="gearbox" style="width: 180px;">Gearbox</label><br>
    <select name="gearbox" id="gearbox" v-model="gearbox" @change="fetchPnoSpecifics" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);">
      <option value="">All</option>
      <option v-for="gearbox in gearboxes" :key="gearbox" :value="gearbox">{{ gearbox }}</option>
    </select>

    <br><br>
      <label class="displaytable" style="width: 180px;">Display Table</label><br>
      <select name="displaytable" v-model="displaytable" id="displaytable" @change="fetchPnoSpecifics" style="display:block;width:180px; height:30px; position: absolute; left: 50%; transform: translate(-50%);" :disabled="this.pnoStore.model_year === '0'">
        <option disabled value="">Please Select...</option>
        <option value="Model">Model</option>       
        <option value="Engine">Engine</option>
        <option value="SalesVersion">Sales Version</option> 
        <option value="Gearbox">Gearbox</option>
        <option value="Features">Features</option>
        <option value="Colors">Colors</option>
        <option value="Options">Options</option>
        <option value="Upholstery">Upholstery</option>
      </select>

    <br><br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" @click="reset">Reset Filters</button>
    <br><br>
    <hr class ="divider">

    <span style="font-size: 32px;">Manage Sources</span><br><br>

    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" onclick="document.getElementById('getFile').click()">Upload VISA file</button>
    <input type='file' class="visaupload" id="getFile" ref="file" style="display:none" accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" v-on:change="uploadVisa">
    <br><br><br>
    <button style="display:block;width:180px; height:50px; position: absolute; left: 50%; transform: translate(-50%);" @click="refreshCPAM">Refresh CPAM data</button>

    <br><br><br>
    <div class="country">
      <label for="country">Change Country: </label>
      <select v-model="selectedCountry" @change="changeCountry(selectedCountry)">
        <option disabled value="">Germany</option>
        <option v-for="country in countries" :key="country" :value="country">
          {{ country }}
        </option>
      </select>
    </div>

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
      <tr v-for="pno in listModels" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">
          {{ pno.MarketText }}
        </td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @change="pushUpdateModel(pno)" />
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
      <tr v-for="pno in listSalesversions" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">
          {{ pno.MarketText }}
        </td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @change="pushUpdateSV(pno)" />
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
        <th>Type</th>
        <th>Performance in kW (PS)</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in listEngines" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">
          {{ pno.MarketText }}
        </td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @change="pushUpdateEngine(pno)" />
        </td>
        <td>
          <input type="EngineCategory" v-model="pno.EngineCategory" @input="pno.edited = true" @change="pushUpdateEngine(pno)" />
        </td>
        <td>
          <input type="SubCategory" v-model="pno.EngineType" @input="pno.edited = true" @change="pushUpdateEngine(pno)" />
        </td>
        <td>
          <input type="Performance" v-model="pno.Performance" @input="pno.edited = true" @change="pushUpdateEngine(pno)" />
        </td>
      </tr>
    </tbody>
  </table>
     <!-- Gearbox Table -->
     <table v-if="displaytable === 'Gearbox'">
    <thead>
      <tr>
        <th>Engine</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in listGearboxes" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">
          {{ pno.MarketText }}
        </td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @change="pushUpdateGearbox(pno)" />
        </td>
      </tr>
    </tbody>
  </table>
  <!-- Features Table -->
  <table v-if="displaytable === 'Features'">
    <thead>
      <tr>
        <th>Feature</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableFeatures" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.MarketText }}</td>
        <td>
          <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
      </tr>
    </tbody>
  </table>
    <!-- Colors Table -->
    <table v-if="displaytable === 'Colors'">
    <thead>
      <tr>
        <th>Color</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableColors" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.MarketText }}</td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
      </tr>
    </tbody>
  </table>
      <!-- Options Table -->
      <table v-if="displaytable === 'Options'">
    <thead>
      <tr>
        <th>Option</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableOptions" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.MarketText }}</td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
      </tr>
    </tbody>
  </table>
      <!-- Upholstery Table -->
      <table v-if="displaytable === 'Upholstery'">
    <thead>
      <tr>
        <th>Upholstery</th>
        <th>CPAM Text</th>
        <th>Market Text</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="pno in tableUpholstery" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
        <td class="CPAMColumn" style="background-color: #f4f4f4;">{{ pno.MarketText }}</td>
        <td>
          <input type="MarketText" v-model="pno.CountryText" @input="pno.edited = true" @click="startEditing(pno)" />
        </td>
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
        entitiesStore: useEntitiesStore(),
        countries: [],
        selectedCountry: '',
      }
    },
    async created() {
      this.pnoStore.model_year = '0';
      this.entitiesStore.model_year = '0';

      await this.pnoStore.fetchSupportedCountries().then(() => {
        console.log('Supported countries fetched')
      }).catch((error) => {
        console.error('Error fetching countries', error)
      })

      await this.pnoStore.fetchAvailableModelYears().then(() => {
        console.log('Available model years fetched')
      }).catch((error) => {
        console.error('Error fetching available model years', error)
      })
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
      model_text() {
        return this.entitiesStore.models
      },
      engines_text() {
        return this.entitiesStore.engines
      },
      salesversion_text() {
        return this.entitiesStore.salesversions
      },
      gearboxes_text() {
        return this.entitiesStore.gearboxes
      },
      // Unique values for tables
      listModels() {
        let models = this.entitiesStore.models;
        let filteredModels = models.filter(models => {
          return this.tableFilteredPnos().some(pno => pno.Model === models.Code);
        });
        return filteredModels;
      },
      listEngines() {
        let en = this.entitiesStore.engines;
        let filteredEn = en.filter(en => {
          return this.tableFilteredPnos().some(pno => pno.Engine === en.Code);
        });
        return filteredEn;
      },
      listSalesversions() {
        let sv = this.entitiesStore.salesversions;
        let filteredSv = sv.filter(sv => {
          return this.tableFilteredPnos().some(pno => pno.SalesVersion === sv.Code);
        });
        return filteredSv;
      },
      listGearboxes() {
        let gearboxes = this.entitiesStore.gearboxes;
        let filteredGearboxes = gearboxes.filter(gearboxes => {
          return this.tableFilteredPnos().some(pno => pno.Gearbox === gearboxes.Code);
        });
        return filteredGearboxes;
      },
      tableFeatures() {
        return this.pnoStore.pnosFeatures
      },
      tableColors() {
        return this.pnoStore.pnosColors
      },
      tableUpholstery() {
        return this.pnoStore.pnosUpholstery
      },
      tableOptions() {
        return this.pnoStore.pnosOptions
      },
    },
  methods: {

    tableFilteredPnos() {
        return this.pnoStore.filteredPnos(this.model, this.engine, this.salesversion, this.gearbox)
      },

    refreshModelyear() {
      this.pnoStore.model_year = this.model_year
      this.entitiesStore.model_year = this.model_year
      console.log(this.model_year)
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

      this.fetchEntities();

    },

    async fetchEntities() {
      try {
        await this.pnoStore.fetchPnos();
        console.log('PNOs fetched');
        await this.entitiesStore.fetchModels();
        console.log('Model text fetched');
        await this.entitiesStore.fetchEngines();
        console.log('Engine text fetched');
        await this.entitiesStore.fetchSalesversions();
        console.log('Salesversion text fetched');
        await this.entitiesStore.fetchGearboxes();
        console.log('Gearboxes text fetched');
      } catch (error) {
        console.error('Error fetching data', error);
      }
    },

    async fetchPnoSpecifics() {
      delete this.originalData;
      try {
        if (this.displaytable === 'Features') {
          await this.pnoStore.fetchPnosFeatures(this.model, this.engine, this.salesversion, this.gearbox);
          console.log('PNO Features fetched');
        }
        if (this.displaytable === 'Colors') {
          await this.pnoStore.fetchPnosColors(this.model, this.engine, this.salesversion, this.gearbox);
          console.log('PNO Colors fetched');
        }
        if (this.displaytable === 'Options') {
          await this.pnoStore.fetchPnosOptions(this.model, this.engine, this.salesversion, this.gearbox);
          console.log('PNO Options fetched');
        }
        if (this.displaytable === 'Upholstery') {
          await this.pnoStore.fetchPnosUpholstery(this.model, this.engine, this.salesversion, this.gearbox);
          console.log('PNO Upholstery fetched');
        }
      } catch (error) {
        console.error('Error fetching data', error);
      }
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
      this.entitiesStore.pushUpdateModel(pno.Code, pno.MarketText)
      pno.edited = false
    },
    pushUpdateEngine(pno) {
      console.log(pno);
      this.entitiesStore.pushUpdateEngine(pno.Code, pno.CountryText, pno.EngineCategory, pno.EngineType, pno.Performance)
      pno.edited = false
    },
    pushUpdateSV(pno) {
      this.entitiesStore.pushUpdateSV(pno.Code, pno.MarketText)
      pno.edited = false
    },
    pushUpdateGearbox(pno) {
      this.entitiesStore.pushUpdateGearbox(pno.Code, pno.MarketText)
      pno.edited = false
    },
    uploadVisa() {
      const file = this.$refs.file.files[0];
      console.log(file)
      const formData = new FormData();
      formData.append('visa', file);
      index.post(`/${this.pnoStore.country}/ingest/visa/upload`, formData);
    },
    refreshCPAM() {
      index.get('/ingest/cpam');
    },
    changeCountry(newCountry) {
      this.pnoStore.setCountry(newCountry);
      this.entitiesStore.setCountry(newCountry);
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

  td {
  width: 200px;

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

  /* .country {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    color: black;
    font-size: 0.8em;
    margin-left: 1rem;
  } */

  /* @media (max-width: 1024px) {
    .sidebar {
    display: none;
    }
  } */

  </style>