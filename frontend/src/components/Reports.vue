<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">Reports</span>
    <!-- Table Selection -->
    <label class="displaytable" style="width: 180px;">Report Type</label><br>
    <select name="displaytable" v-model="displaytable" id="displaytable"
      @change="fetchLog()" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select...</option>
      <option value="Changelog">Data Changelog</option>
      <option value="WARNING">Price Warnings</option>
      <option value="ERROR">Technical Errors</option>
    </select>
    <!-- Export Technical Log Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top: 50px;"
      @click="exportTechnicalLog">Export Technical Log</button>
  </aside>
  <main class="main-content">
    <!-- Changelog Table -->
    <table v-if="displaytable === 'Changelog'">
      <thead v-if="log.length >= 1">
        <tr>
          <th>Date</th>
          <th>Model</th>
          <th>Engine</th>
          <th>Sales Version</th>
          <th>Gearbox</th>
          <th>Table</th>
          <th>Field</th>
          <th>From</th>
          <th>To</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in log" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td class="ChangeDate" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeDate }}</td>
          <td class="Model" style="background-color: #f4f4f4; text-align: left;">{{ pno.Model }}</td>
          <td class="Engine" style="background-color: #f4f4f4; text-align: left;">{{ pno.Engine }}</td>
          <td class="SalesVersion" style="background-color: #f4f4f4; text-align: left;">{{ pno.SalesVersion }}</td>
          <td class="Gearbox" style="background-color: #f4f4f4; text-align: left;">{{ pno.Gearbox }}</td>
          <td class="ChangeTable" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeTable }}</td>
          <td class="ChangeField" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeField }}</td>
          <td class="ChangeFrom" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeFrom }}</td>
          <td class="ChangeTo" style="background-color: #f4f4f4; text-align: left;">{{ pno.ChangeTo }}</td>
        </tr>
      </tbody>
    </table>
    <!-- Pricing and Technical Error Table -->
    <table v-if="displaytable === 'ERROR' || displaytable === 'WARNING'">
      <thead v-if="log.length >= 1">
        <tr>
          <th>Date</th>
          <th>Message</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in log" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td class="LogDate" style="background-color: #f4f4f4; text-align: left;">{{ pno.LogDate }}</td>
          <td class="LogMessage" style="background-color: #f4f4f4; text-align: left;">{{ pno.LogMessage }}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>



<script>
import { useEntitiesStore } from '../stores/entities.js'
import axios from '../api/index.js'
import index from '../api/index.js'

export default {
  name: 'ReportsView',
  data() {
    return {
      displaytable: '',
      log: [],
      entitiesStore: useEntitiesStore(),
      selectedCountry: '',
    }
  },
  async created() {
    this.selectedCountry = this.entitiesStore.country;
    this.log = [];
  },
  methods: {

    async fetchLog() {
      this.log = [];
      let path = '';
      if (this.displaytable === 'Changelog') {
        path = `/db/${this.selectedCountry.Code}/0/changelog`
      }
      if (this.displaytable === 'WARNING' || this.displaytable === 'ERROR') {
        path = `/db/${this.selectedCountry.Code}/0/dq-log?&LogType=${this.displaytable}`
      }
      return await index.get(path).then((response) => {
        response.data.forEach(item => {
          if (this.displaytable === 'Changelog') {
            let date = new Date(item.ChangeDate);
            item.ChangeDate = date.toISOString().replace('T', ' ').substring(0, 19);
          }
          if (this.displaytable === 'WARNING' || this.displaytable === 'ERROR') {
            let date = new Date(item.LogDate);
            item.LogDate = date.toISOString().replace('T', ' ').substring(0, 19);
          }
        });
        this.log = response.data;
      }).catch((error) => {
        console.error('Error fetching changelog:', error)
      })
    },
    async exportTechnicalLog() {
      const link = document.createElement('a');
      link.href = `${axios.endpoint}/${this.selectedCountry.Code}/export/technical-logs`;
      link.setAttribute('download', 'Technical_Log.zip');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
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
  height: calc(100vh - 4rem - 100px);
  /* Adjust as needed */
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

.model,
.modelyear,
.displaytable {
  text-align: left;
  display: inline-block;
  width: 180px;
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