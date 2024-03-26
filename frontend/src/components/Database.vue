<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">PNO</span>
    <!-- Table Selection -->
    <label class="displaytable" style="width: 180px;">Display Table</label><br>
    <select name="displaytable" v-model="displaytable" id="displaytable" @change="fetchPnoSpecifics(); displaytablereset()" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select...</option>
      <option value="Model">Model</option>       
      <option value="Engine">Engine</option>
      <option value="SalesVersion">Sales Version</option> 
      <option value="Gearbox">Gearbox</option>
      <option value="Features" :disabled="this.pnoStore.model_year === ''">Features</option>
      <option value="Colors" :disabled="this.pnoStore.model_year === ''">Colors</option>
      <option value="Options" :disabled="this.pnoStore.model_year === ''">Options</option>
      <option value="Upholstery" :disabled="this.pnoStore.model_year === ''">Upholstery</option>
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
    <select name="model" id="model" v-model="model" @change="fetchPnoSpecifics" style="width:180px; height:30px; position: absolute;" :disabled="!['Model', 'Features', 'Colors', 'Options','Upholstery'].includes(displaytable) || model_year === '0'">
      <option value="" :disabled="!['Model', 'Engine', 'SalesVersion', 'Gearbox'].includes(displaytable)">All</option>
      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
    </select>
    <!-- Filter for engines -->
    <label class="engine" style="width: 180px;">Engine</label><br>
    <select name="engine" id="engine" v-model="engine" @change="fetchPnoSpecifics" style="width:180px; height:30px; position: absolute;" :disabled="!['Engine'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="engine in engines" :key="engine" :value="engine">{{ engine }}</option>
    </select>
    <!-- Filter for salesversions -->
    <label class="salesversion" style="width: 180px;">Sales Version</label><br>
    <select name="salesversion" id="salesversion" v-model="salesversion" @change="fetchPnoSpecifics" style="width:180px; height:30px; position: absolute;" :disabled="!['SalesVersion'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="salesversion in salesversions" :key="salesversion" :value="salesversion">{{ salesversion }}</option>
    </select>
    <!-- Filter for gearboxes -->
    <label class="gearbox" style="width: 180px;">Gearbox</label><br>
    <select name="gearbox" id="gearbox" v-model="gearbox" @change="fetchPnoSpecifics" style="width:180px; height:30px; display: inline-block; position: absolute;" :disabled="!['Gearbox'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="gearbox in gearboxes" :key="gearbox" :value="gearbox">{{ gearbox }}</option>
    </select>

    <!-- Filter Reset Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top: 64px;" @click="reset">Reset Filters</button>

    <hr class ="divider" style="margin-top: 40px;">

    <span style="font-size: 32px;">Manage Sources</span>
    <!-- VISA Upload Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top:20px;" onclick="document.getElementById('getFile').click()">Upload VISA file</button>
    <input type='file' class="visaupload" id="getFile" ref="file" style="display:none" accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" v-on:change="uploadVisa">
    
    <!-- CPAM Refresh Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top:10px;" @click="refreshCPAM">Refresh CPAM data</button>

    <!-- Country Select Dropdown Menu -->
    <div class="country bottom-div">
      <label for="country" class="countrylabel">Change Country: </label>
      <select v-model="selectedCountry" @change="changeCountry(this.selectedCountry)">
        <option value="231" selected disabled>Germany</option>
      </select>
    </div>
  </aside>
  <main class="main-content">
    <!-- Model Table -->
    <table v-if="displaytable === 'Model' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th v-if="model_year === ''">Model Year</th>
          <th>Model</th>
          <th>CPAM Text</th>
          <th>Market Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableModels" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td v-if="model_year === ''">
            {{ pno.model_year }}
          </td>
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.MarketText }}
          </td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateModel(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Salesversion Table -->
    <table v-if="displaytable === 'SalesVersion' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Sales Version</th>
          <th>CPAM Text</th>
          <th>Market Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableSalesversions" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.MarketText }}
          </td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateSV(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Engine Table -->
    <table v-if="displaytable === 'Engine' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
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
        <tr v-for="pno in tableEngines" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.MarketText }}
          </td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateEngine(pno)" />
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
    <table v-if="displaytable === 'Gearbox' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Gearbox</th>
          <th>CPAM Text</th>
          <th>Market Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableGearboxes" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.MarketText }}
          </td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateGearbox(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Features Table -->
    <table v-if="displaytable === 'Features' && model_year !== '0' && this.model !== ''">
      <thead v-if="model_year !== '0'">
        <tr>
          <!-- <th v-if="model === ''">Model</th> -->
          <th>Feature</th>
          <th>CPAM Text</th>
          <th>Market Text</th>
          <th>Feature Category</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableFeatures" :key="pno.id" :class="{ 'editing': pno.edited }">
          <!-- <td v-if="model === ''">
            {{ pno.model }}
          </td> -->
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateFeature(pno)" />
          </td>
          <td>
            <input type="Category" v-model="pno.CustomCategory" @input="pno.edited = true" @change="pushUpdateFeature(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Colors Table -->
    <table v-if="displaytable === 'Colors' && model_year !== '0' && this.model !== ''">
      <thead v-if="model_year !== '0'">
        <tr>
          <!-- <th v-if="model === ''">Model</th> -->
          <th>Color</th>
          <th>CPAM Text</th>
          <th>Market Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableColors" :key="pno.id" :class="{ 'editing': pno.edited }">
          <!-- <td v-if="model === ''">
            {{ pno.model }}
          </td> -->
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true" @change="pushUpdateColor(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Options Table -->
    <table v-if="displaytable === 'Options' && model_year !== '0' && this.model !== ''">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Option (Feature)</th>
          <th>Feature Text</th>
          <th>Feature Category</th>
          <th>CPAM Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableOptions" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td style="background-color: #f4f4f4;">{{ pno.Feature }}</td>
          <td class="FeatureColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.FeatureText }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
        </tr>
      </tbody>
    </table>
    <!-- Upholstery Table -->
    <table v-if="displaytable === 'Upholstery' && model_year !== '0' && this.model !== ''">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Upholstery (Feature)</th>
          <th>Feature Text</th>
          <th>Feature Category</th>
          <th>CPAM Text</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableUpholstery" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="FeatureColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.FeatureText }}</td>
          <td class="Category" style="background-color: #f4f4f4; text-align: left;">{{ pno.Category }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
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
    countries() {
      return this.pnoStore.supported_countries
    },
    // Unique values for tables
    tableModels() {
      if (this.model === "") {
        return this.entitiesStore.models;
      }
      return this.entitiesStore.models.filter(model => model.Code === this.model)
    },
    tableEngines() {
      if (this.engine === "") {
        return this.entitiesStore.engines;
      }
      return this.entitiesStore.engines.filter(engine => engine.Code === this.engine)
    },
    tableSalesversions() {
      if (this.salesversion === "") {
        return this.entitiesStore.salesversions;
      }
      return this.entitiesStore.salesversions.filter(salesversion => salesversion.Code === this.salesversion)
    },
    tableGearboxes() {
      if (this.gearbox === "") {
        return this.entitiesStore.gearboxes;
      }
      return this.entitiesStore.gearboxes.filter(gearbox => gearbox.Code === this.gearbox)
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
      if (this.displaytable === 'Model' || this.displaytable === 'Features' || this.displaytable === 'Colors' || this.displaytable === 'Options' || this.displaytable === 'Upholstery') {
      await this.entitiesStore.fetchModels();
      console.log('Model text fetched');
      }
      if (this.displaytable === 'Engine') {
      await this.entitiesStore.fetchEngines();
      console.log('Engine text fetched');
      }
      if (this.displaytable === 'SalesVersion') {
      await this.entitiesStore.fetchSalesversions();
      console.log('Salesversion text fetched');
      }
      if (this.displaytable === 'Gearbox') {
      await this.entitiesStore.fetchGearboxes();
      console.log('Gearboxes text fetched');
      }
    } catch (error) {
      console.error('Error fetching data', error);
    }
  },

  async fetchPnoSpecifics() {
    try {
      if (this.displaytable === 'Features' && this.model !== '') {
        await this.pnoStore.fetchPnosFeatures(this.model, this.engine, this.salesversion, this.gearbox);
        console.log('PNO Features fetched');
      }
      if (this.displaytable === 'Colors' && this.model !== '') {
        await this.pnoStore.fetchPnosColors(this.model, this.engine, this.salesversion, this.gearbox);
        console.log('PNO Colors fetched');
      }
      if (this.displaytable === 'Options' && this.model !== '') {
        await this.pnoStore.fetchPnosOptions(this.model, this.engine, this.salesversion, this.gearbox);
        console.log('PNO Options fetched');
      }
      if (this.displaytable === 'Upholstery' && this.model !== '') {
        await this.pnoStore.fetchPnosUpholstery(this.model, this.engine, this.salesversion, this.gearbox);
        console.log('PNO Upholstery fetched');
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
    await this.pnoStore.setModelYear('0');
  },
  async displaytablereset() {
    this.model_year = '0';
    this.model = '';
    this.engine = '';
    this.salesversion = '';
    this.gearbox = '';
    await this.pnoStore.setModelYear('0');
  },
  // Non-PNO-specific updates
  pushUpdateModel(pno) {
    this.entitiesStore.pushUpdateModel(pno.Code, pno.CustomName)
    pno.edited = false
  },
  pushUpdateEngine(pno) {
    this.entitiesStore.pushUpdateEngine(pno.Code, pno.CustomName, pno.EngineCategory, pno.EngineType, pno.Performance)
    pno.edited = false
  },
  pushUpdateSV(pno) {
    this.entitiesStore.pushUpdateSV(pno.Code, pno.CustomName)
    pno.edited = false
  },
  pushUpdateGearbox(pno) {
    this.entitiesStore.pushUpdateGearbox(pno.Code, pno.CustomName)
    pno.edited = false
  },
  // PNO-specific updates
  pushUpdateFeature(pno) {
    this.pnoStore.pushUpdateFeature(this.model, pno.Code, pno.CustomName, pno.CustomCategory)
    pno.edited = false
  },
  pushUpdateColor(pno) {
    this.pnoStore.pushUpdateColor(this.model, pno.Code, pno.CustomName)
    pno.edited = false
  },
  // Database updates 
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
  async changeCountry(newCountry) {
    await this.pnoStore.setCountry(newCountry);
    await this.entitiesStore.setCountry(newCountry);
  },
}
};

</script>
  
<style scoped>


.main-content {
  padding: 2rem;
  flex-grow: 1;
  overflow: auto;
  height: calc(100vh - 4rem - 100px); /* Adjust as needed */
}
.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 1rem;
  /* min-height: 1030px; */
  position:relative;
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

.model, .modelyear, .engine, .salesversion, .gearbox, .displaytable {
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