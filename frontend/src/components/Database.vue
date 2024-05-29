<template>
  <aside class="sidebar">
    <span class="title" style="font-size: 32px;">PNO</span>
    <!-- Table Selection -->
    <label class="displaytable" style="width: 180px;">Display Table</label><br>
    <select name="displaytable" v-model="displaytable" id="displaytable"
      @change="fetchPnoSpecifics(); displaytablereset()" style="width:180px; height:30px; position: absolute;">
      <option disabled value="">Please Select...</option>
      <option value="Model">Model</option>
      <option value="Engine">Engine</option>
      <option value="SalesVersion">Sales Version</option>
      <option value="Gearbox">Gearbox</option>
      <option value="Features" :disabled="this.pnoStore.model_year === ''">Features</option>
      <option value="Options" :disabled="this.pnoStore.model_year === ''">Options</option>
      <option value="Colors" :disabled="this.pnoStore.model_year === ''">Colors</option>
      <option value="Upholstery" :disabled="this.pnoStore.model_year === ''">Upholstery</option>
      <option value="Packages" :disabled="this.pnoStore.model_year === ''">Packages</option>
      <option value="VISA Files" :disabled="this.pnoStore.model_year === ''">VISA Files</option>
      <option value="Sales Channels" :disabled="this.pnoStore.model_year === ''">Sales Channels</option>
    </select>
    <!-- Filter for model years -->
    <label class="modelyear" style="width: 180px;">Model Year</label><br>
    <select name="model_year" id="model_year" v-model="model_year" @change="refreshModelyear(); fetchPnoSpecifics()"
      style="width:180px; height:30px; position: absolute;" :disabled="displaytable === ''">
      <option disabled value="0">Please Select...</option>
      <option value="0000" :disabled="!['Model', 'Engine', 'SalesVersion', 'Gearbox'].includes(displaytable)">All
      </option>
      <option v-for="model_year in model_years" :key="model_year" :value="model_year">{{ model_year }}</option>
    </select>
    <!-- Filter for models -->
    <label class="model" style="width: 180px;">Model</label><br>
    <select name="model" id="model" v-model="model" @change="fetchPnoSpecifics"
      style="width:180px; height:30px; position: absolute;"
      :disabled="!['Model', 'Features', 'Colors', 'Options', 'Upholstery', 'Packages'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="model in models.sort()" :key="model" :value="model">{{ model }}</option>
    </select>
    <!-- Filter for engines -->
    <label class="engine" style="width: 180px;">Engine</label><br>
    <select name="engine" id="engine" v-model="engine" @change="fetchPnoSpecifics"
      style="width:180px; height:30px; position: absolute;"
      :disabled="!['Engine'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="engine in engines.sort()" :key="engine" :value="engine">{{ engine }}</option>
    </select>
    <!-- Filter for salesversions -->
    <label class="salesversion" style="width: 180px;">Sales Version</label><br>
    <select name="salesversion" id="salesversion" v-model="salesversion" @change="fetchPnoSpecifics"
      style="width:180px; height:30px; position: absolute;"
      :disabled="!['SalesVersion'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="salesversion in salesversions.sort()" :key="salesversion" :value="salesversion">{{ salesversion }}
      </option>
    </select>
    <!-- Filter for gearboxes -->
    <label class="gearbox" style="width: 180px;">Gearbox</label><br>
    <select name="gearbox" id="gearbox" v-model="gearbox" @change="fetchPnoSpecifics"
      style="width:180px; height:30px; display: inline-block; position: absolute;"
      :disabled="!['Gearbox'].includes(displaytable) || model_year === '0'">
      <option value="">All</option>
      <option v-for="gearbox in gearboxes.sort()" :key="gearbox" :value="gearbox">{{ gearbox }}</option>
    </select>

    <!-- Filter Reset Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top: 64px;"
      @click="reset">Reset Filters</button>

    <hr class="divider" style="margin-top: 40px;">

    <span style="font-size: 32px;">Manage Sources</span>
    <!-- VISA Upload Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top:20px;"
      onclick="document.getElementById('getFile').click()">Upload VISA file</button>
    <input type='file' class="visaupload" id="getFile" ref="file" style="display:none"
      accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" v-on:change="uploadVisa">

    <!-- CPAM Refresh Button -->
    <button style="display:block;width:180px; height:50px; display: inline-block; margin-top:10px;"
      @click="refreshCPAM">Refresh CPAM data</button>

    <!-- Country Select Dropdown Menu -->
    <div class="country bottom-div">
      <label for="country" class="countrylabel">Change Country: </label>
      <select v-model="selectedCountry" @change="changeCountry(this.selectedCountry)">
        <option value="231" selected disabled>Germany</option>
      </select>
    </div>
  </aside>
  <main class="main-content">
    <!-- Table Filter -->
    <div style="display: flex; margin-bottom: 1em;">
      <input v-if="displaytable !== '' && model_year !== '0' && !customFeatureTable && !discountTable && !xCodesTable"
        v-model="searchTerm" type="text" placeholder="Filter" style="margin-right: 1ch;">
      <!-- Add Custom Feature -->
      <button v-if="displaytable === 'Features' && model_year !== '0' && !customFeatureTable"
        @click="showCustomFeatureTable">Add custom feature</button>
      <!-- Upload Visa File -->
      <button v-if="displaytable === 'VISA Files' && model_year !== '0'" @click="$refs.file.click()">Upload VISA
        file</button>
      <input type='file' class="visaupload" id="getFile" ref="file" style="display:none"
        accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" @change="uploadVisa">
      <!-- Displaying discounts for sales channel -->
      <div v-if="displaytable === 'Sales Channels' && model_year !== '0' && discountTable"><strong>[{{
      this.activeSalesChannel.Code + " " + this.activeSalesChannel.ChannelName }}]</strong> Discounts</div>
      <div v-if="displaytable === 'Sales Channels' && model_year !== '0' && xCodesTable"><strong>[{{
      this.activeSalesChannel.Code + " " + this.activeSalesChannel.ChannelName }}]</strong> X-Codes</div>
      <button v-if="(discountTable || xCodesTable) && model_year !== '0'"
        @click="this.discountTable = false, this.xCodesTable = false, this.selectedRow = null, this.newsaleschannel = [], this.newdiscount = [], this.newcustomlocaloption = []"
        style="margin-left: 10px;">Return to Sales Channels</button>
    </div>

    <!-- Model Table -->
    <table v-if="displaytable === 'Model' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Model
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
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
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdateModel(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Salesversion Table -->
    <table v-if="displaytable === 'SalesVersion' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Sales Version
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
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
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Engine
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Category
              <div style="margin-left: 1ch;">
                <span @click="sortTable('EngineCategory', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('EngineCategory', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Type
              <div style="margin-left: 1ch;">
                <span @click="sortTable('EngineType', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('EngineType', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Performance kW(PS)
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Performance', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Performance', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
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
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdateEngine(pno)" />
          </td>
          <td>
            <input type="EngineCategory" v-model="pno.EngineCategory" @input="pno.edited = true"
              @change="pushUpdateEngine(pno)" />
          </td>
          <td>
            <input type="SubCategory" v-model="pno.EngineType" @input="pno.edited = true"
              @change="pushUpdateEngine(pno)" />
          </td>
          <td>
            <input type="Performance" v-model="pno.Performance" @input="pno.edited = true"
              @change="pushUpdateEngine(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Gearbox Table -->
    <table v-if="displaytable === 'Gearbox' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Gearbox
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
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
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdateGearbox(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Features Table -->
    <table v-if="displaytable === 'Features' && model_year !== '0' && !customFeatureTable">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Feature
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Feature Category
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomCategory', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomCategory', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">Action</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableFeatures" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">
            <input v-if="pno.ID !== null" v-model="pno.Code" type="text" @input="pno.edited = true" @change="pushUpdateFeature(pno)" />
            <span v-else>{{ pno.Code }}</span>
          </td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">
            <input v-if="pno.ID !== null" v-model="pno.MarketText" type="text" @input="pno.edited = true" @change="pushUpdateFeature(pno)" />
            <span v-else>{{ pno.MarketText }}</span>
          </td>
          <td>
            <input v-model="pno.CustomName" type="text" @input="pno.edited = true" @change="pushUpdateFeature(pno)" />
          </td>
          <td>
            <input v-model="pno.CustomCategory" type="text" @input="pno.edited = true"
              @change="pushUpdateFeature(pno)" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span v-if="pno.ID !== null" @click="deleteCustomFeature(pno)" style="cursor: pointer; color: red;">[X]</span>
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Custom Feature Table -->
    <table v-if="customFeatureTable">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>Market Text</th>
          <th>Feature Category</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><input type="text" v-model="newEntry.CustomName" /></td>
          <td><input type="text" v-model="newEntry.CustomCategory" /></td>
          <td><input type="text" v-model="newEntry.StartDate"
              pattern="\d{4}(0[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-3])" /></td>
          <td><input type="text" v-model="newEntry.EndDate"
              pattern="\d{4}(0[1-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-3])" /></td>
        </tr>
      </tbody>
    </table>

    <div style="display: flex; justify-content: flex-start;">
      <!-- Save Custom Feature Button -->
      <div>
        <button v-if="customFeatureTable" :disabled="!isFormValid" @click="pushNewCustomFeature(newEntry)"
          style="margin-left: 5px;">Save custom feature</button>
      </div>
      <!-- Return to Features Button -->
      <div style="margin-left: 10px;">
        <button v-if="customFeatureTable && model_year !== '0'" @click="showCustomFeatureTable">Return to
          features</button>
      </div>
    </div>

    <!-- Colors Table -->
    <table v-if="displaytable === 'Colors' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Color
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableColors" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdateColor(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Options Table -->
    <table v-if="displaytable === 'Options' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Option (Feature)
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Feature Category
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomCategory', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomCategory', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableOptions" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td style="background-color: #f4f4f4; text-align: left;">
            <input v-if="!pno.hasFeature" v-model="pno.CustomName" type="text" @input="pno.edited = true"
              @change="pushUpdateOption(pno)" />
            <span v-else>{{ pno.CustomName }}</span>
          </td>
          <td class="FeatureColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.CustomCategory }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
        </tr>
      </tbody>
    </table>
    <!-- Upholstery Table -->
    <table v-if="displaytable === 'Upholstery' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Upholstery
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Category
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Category', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Category', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tableUpholstery" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdateUpholstery(pno)" />
          </td>
          <td>
            <!-- <input type="UpholsteryCategory" v-model="pno.Category" @input="pno.edited = true" @change="pushUpdateUpholstery(pno)" />    -->
            <input type="UpholsteryCategory" v-model="pno.CustomCategory" @input="pno.edited = true"
              @change="pushUpdateUpholstery(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Packages Table -->
    <table v-if="displaytable === 'Packages' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Package
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              CPAM Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('MarketText', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('MarketText', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Market Text
              <div style="margin-left: 1ch;">
                <span @click="sortTable('CustomName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('CustomName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in tablePackages" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td style="background-color: #f4f4f4;">{{ pno.Code }}</td>
          <td class="CPAMColumn" style="background-color: #f4f4f4; text-align: left;">{{ pno.MarketText }}</td>
          <td>
            <input type="MarketText" v-model="pno.CustomName" @input="pno.edited = true"
              @change="pushUpdatePackage(pno)" />
          </td>
        </tr>
      </tbody>
    </table>
    <!-- VISA File Table -->
    <table v-if="displaytable === 'VISA Files' && model_year !== '0'">
      <thead v-if="model_year !== '0'">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Name
              <div style="margin-left: 1ch;">
                <span @click="sortTable('file_name', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('file_name', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in visa_files" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td class="VISAColumn" style="background-color: #f4f4f4; text-align: left;">
            {{ pno.file_name }}
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="deleteVISAFile(pno.file_name)" style="cursor: pointer; color: red;">[X]</span>
          </td>
        </tr>
      </tbody>
    </table>
    <!-- Sales Channels Table -->
    <table v-if="displaytable === 'Sales Channels' && model_year !== '0' && !discountTable && !xCodesTable">
      <thead v-if="model_year !== '0' && (sales_channels.length > 0 || this.newsaleschannel.length >= 1) ">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Code
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Code', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Code', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Name
              <div style="margin-left: 1ch;">
                <span @click="sortTable('ChannelName', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('ChannelName', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Comment
              <div style="margin-left: 1ch;">
                <span @click="sortTable('Comment', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('Comment', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Start Date
              <div style="margin-left: 1ch;">
                <span @click="sortTable('StartDate', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('StartDate', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              End Date
              <div style="margin-left: 1ch;">
                <span @click="sortTable('EndDate', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('EndDate', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in sales_channels" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td>
            <input type="Code" v-model="pno.Code" @input="pno.edited = true" @change="pushUpdateSalesChannel(pno)" />
          </td>
          <td>
            <input type="ChannelName" v-model="pno.ChannelName" @input="pno.edited = true"
              @change="pushUpdateSalesChannel(pno)" />
          </td>
          <td>
            <input type="Comment" v-model="pno.Comment" @input="pno.edited = true"
              @change="pushUpdateSalesChannel(pno)" />
          </td>
          <td>
            <input type="StartDate" v-model="pno.StartDate" @input="pno.edited = true"
              @change="pushUpdateSalesChannel(pno)" />
          </td>
          <td>
            <input type="EndDate" v-model="pno.EndDate" @input="pno.edited = true"
              @change="pushUpdateSalesChannel(pno)" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="fetchDiscounts(pno)" style="cursor: pointer; margin-right: 10px;">[%]</span>
            <span @click="fetchXCodes(pno)" style="cursor: pointer; margin-right: 10px;">[X-Codes]</span>
            <span @click="deleteSalesChannel(pno)" style="cursor: pointer; color: red;">[X]</span>
          </td>
        </tr>
      </tbody>
      <tbody>
        <tr v-for="pno in newsaleschannel" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td>
            <input type="Code" v-model="pno.Code" @input="pno.edited = true" />
          </td>
          <td>
            <input type="ChannelName" v-model="pno.ChannelName" @input="pno.edited = true" />
          </td>
          <td>
            <input type="Comment" v-model="pno.Comment" @input="pno.edited = true" />
          </td>
          <td>
            <input type="StartDate" v-model="pno.StartDate" @input="pno.edited = true" />
          </td>
          <td>
            <input type="EndDate" v-model="pno.EndDate" @input="pno.edited = true" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="createSalesChannel(pno)" style="cursor: pointer;">[Save]</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="displaytable === 'Sales Channels' && model_year !== '0' && !discountTable && !xCodesTable"
      style="text-align: left; margin-left: 5px;">
      <button @click="addSalesChannel">Add Sales Channel</button>
    </div>
    <!-- Discount Table -->
    <table v-if="displaytable === 'Sales Channels' && model_year !== '0' && discountTable">
      <thead v-if="model_year !== '0' && (discounts.length > 0 || this.newdiscount.length >= 1)">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Discount %
              <div style="margin-left: 1ch;">
                <span @click="sortTable('DiscountPercentage', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('DiscountPercentage', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Retail Price
              <div style="margin-left: 1ch;">
                <span @click="sortTable('RetailPrice', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('RetailPrice', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Wholesale Price
              <div style="margin-left: 1ch;">
                <span @click="sortTable('WholesalePrice', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('WholesalePrice', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Affected Visa Files
              <div style="margin-left: 1ch;">
                <span @click="sortTable('AffectedVisaFile', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('AffectedVisaFile', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              PNO Specific
              <div style="margin-left: 1ch;">
                <span @click="sortTable('PNOSpecific', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('PNOSpecific', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in discounts" :key="pno.id"
          :class="{ 'editing': pno.edited, 'selected': pno.id === selectedRow }">
          <td>
            <input type="DiscountPercentage" v-model="pno.DiscountPercentage" @input="pno.edited = true"
              @change="pushUpdateDiscount(pno)" 
              :disabled="(pno.RetailPrice !== null && pno.RetailPrice !== '') || (pno.WholesalePrice !== null && pno.WholesalePrice !== '')" />
          </td>
          <td>
            <input type="RetailPrice" v-model="pno.RetailPrice" @input="pno.edited = true"
              @change="pushUpdateDiscount(pno)"
              :disabled="pno.DiscountPercentage !== null && pno.DiscountPercentage !== ''" />
          </td>
          <td>
            <input type="WholesalePrice" v-model="pno.WholesalePrice" @input="pno.edited = true"
              @change="pushUpdateDiscount(pno)"
              :disabled="pno.DiscountPercentage !== null && pno.DiscountPercentage !== ''" />
          </td>
          <td>
            <v-select :options="this.entitiesStore.visafiles.map(file => file.file_name)" v-model="pno.AffectedVisaFile" @option:deselected="pushUpdateDiscount(pno)" @option:selected="pushUpdateDiscount(pno)" :reduce="label => label" placeholder="All" multiple></v-select>
          </td>
          <td style="background-color: #f4f4f4;">
            <input type="checkbox" v-model="pno.PNOSpecific" @change="pno.edited = true; pushUpdateDiscount(pno)" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="deleteDiscount(pno)" style="cursor: pointer; color: red;">[X]</span>
          </td>
        </tr>
      </tbody>
      <tbody>
        <tr v-for="pno in newdiscount" :key="pno.id">
          <td>
            <input type="DiscountPercentage" v-model="pno.DiscountPercentage" @input="pno.edited = true" 
            :disabled="(pno.RetailPrice !== null && pno.RetailPrice !== '') || (pno.WholesalePrice !== null && pno.WholesalePrice !== '')" />
          </td>
          <td>
            <input type="RetailPrice" v-model="pno.RetailPrice" @input="pno.edited = true"
              :disabled="pno.DiscountPercentage !== null && pno.DiscountPercentage !== ''" />
          </td>
          <td>
            <input type="WholesalePrice" v-model="pno.WholesalePrice" @input="pno.edited = true"
              :disabled="pno.DiscountPercentage !== null && pno.DiscountPercentage !== ''" />
          </td>
            <v-select :options="this.entitiesStore.visafiles.map(file => file.file_name)" v-model="pno.AffectedVisaFile" @input="handleSelectChange(pno)" :reduce="label => label" placeholder="All" multiple></v-select>
          <td style="background-color: #f4f4f4;">
            <input type="checkbox" v-model="pno.PNOSpecific" @change="pno.edited = true" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="createDiscount(pno)" style="cursor: pointer;">[Save]</span>
            <!-- <span @click="deleteDiscount(pno.ID)" style="cursor: pointer; color: red;">[X]</span> -->
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="displaytable === 'Sales Channels' && model_year !== '0' && discountTable"
      style="text-align: left; margin-left: 5px;">
      <button @click="addDiscount">Add Discount</button>
    </div>
    <!-- X-Codes Table -->
    <table v-if="displaytable === 'Sales Channels' && model_year !== '0' && xCodesTable">
      <thead v-if="model_year !== '0' && (custom_local_options.length > 0 || this.newcustomlocaloption.length >= 1)">
        <tr>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Feature Code
              <div style="margin-left: 1ch;">
                <span @click="sortTable('FeatureCode', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('FeatureCode', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Retail Price
              <div style="margin-left: 1ch;">
                <span @click="sortTable('FeatureRetailPrice', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('FeatureRetailPrice', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th>
            <div style="display: flex; justify-content: center; align-items: center;">
              Wholesale Price
              <div style="margin-left: 1ch;">
                <span @click="sortTable('FeatureWholesalePrice', 1)" style="cursor: pointer;">↑</span>
                <span @click="sortTable('FeatureWholesalePrice', -1)" style="cursor: pointer;">↓</span>
              </div>
            </div>
          </th>
          <th style="width: 10px">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pno in custom_local_options" :key="pno.id" :class="{ 'editing': pno.edited }">
          <td>
            <input type="FeatureCode" v-model="pno.FeatureCode" @input="pno.edited = true"
              @change="pushUpdateXCode(pno)" />
          </td>
          <td>
            <input type="FeatureRetailPrice" v-model="pno.FeatureRetailPrice" @input="pno.edited = true"
              @change="pushUpdateXCode(pno)" />
          </td>
          <td>
            <input type="FeatureWholesalePrice" v-model="pno.FeatureWholesalePrice" @input="pno.edited = true"
              @change="pushUpdateXCode(pno)" />
          </td>
          <td style="background-color: #f4f4f4;">
            <span @click="deleteXCode(pno)" style="cursor: pointer; color: red;">[X]</span>
          </td>
        </tr>
      </tbody>
    </table>
    <tbody>
      <tr v-for="pno in newcustomlocaloption" :key="pno.id" :class="{ 'editing': pno.edited }">
        <td>
          <input type="FeatureCode" v-model="pno.FeatureCode" @input="pno.edited = true" />
        </td>
        <td>
          <input type="FeatureRetailPrice" v-model="pno.FeatureRetailPrice" @input="pno.edited = true" />
        </td>
        <td>
          <input type="FeatureWholesalePrice" v-model="pno.FeatureWholesalePrice" @input="pno.edited = true" />
        </td>
        <td style="background-color: #f4f4f4;">
          <span @click="createXCode(pno)" style="cursor: pointer;">[Save]</span>
        </td>
      </tr>
    </tbody>
    <div v-if="displaytable === 'Sales Channels' && model_year !== '0' && xCodesTable"
      style="text-align: left; margin-left: 5px;">
      <button @click="addCustomLocalOption">Add X-Code</button>
    </div>
  </main>
</template>



<script>
import { usePNOStore } from '../stores/pno.js'
import { useEntitiesStore } from '../stores/entities.js'
import index from '../api/index.js'
import "vue-select/dist/vue-select.css"
import vSelect from "vue-select"

export default {
  name: 'DatabaseView',
  components: {
    vSelect
  },
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
      sortOrder: 1,
      sortColumn: '',
      searchTerm: '',
      customFeatureTable: false,
      discountTable: false,
      xCodesTable: false,
      selectedRow: null,
      activeSalesChannel: [],
      newsaleschannel: [],
      newdiscount: [],
      newcustomlocaloption: [],
      newEntry: {
        Code: '',
        CustomName: '',
        CustomCategory: '',
        StartDate: '',
        EndDate: '',
      },
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
    visa_files() {
      return this.entitiesStore.visafiles.filter(file_name =>
        Object.values(file_name).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    sales_channels() {
      return this.entitiesStore.saleschannels.filter(code =>
        Object.values(code).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    discounts() {
      return this.entitiesStore.discounts.filter(code =>
        Object.values(code).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    custom_local_options() {
      return this.entitiesStore.customlocaloptions.filter(code =>
        Object.values(code).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    // Unique values for tables
    tableModels() {
      let models;
      if (this.model === "") {
        models = this.entitiesStore.models;
      } else {
        models = this.entitiesStore.models.filter(model => model.Code === this.model);
      }
      return models.filter(model =>
        Object.values(model).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableEngines() {
      let engines;
      if (this.engine === "") {
        engines = this.entitiesStore.engines;
      } else {
        engines = this.entitiesStore.engines.filter(engine => engine.Code === this.engine);
      }
      return engines.filter(engine =>
        Object.values(engine).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableSalesversions() {
      let salesversions;
      if (this.salesversion === "") {
        salesversions = this.entitiesStore.salesversions;
      } else {
        salesversions = this.entitiesStore.salesversions.filter(salesversion => salesversion.Code === this.salesversion);
      }
      return salesversions.filter(salesversion =>
        Object.values(salesversion).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableGearboxes() {
      let gearboxes;
      if (this.gearbox === "") {
        gearboxes = this.entitiesStore.gearboxes;
      } else {
        gearboxes = this.entitiesStore.gearboxes.filter(gearbox => gearbox.Code === this.gearbox);
      }
      return gearboxes.filter(gearbox =>
        Object.values(gearbox).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableFeatures() {
      return this.pnoStore.pnosFeatures.filter(feature =>
        Object.values(feature).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableColors() {
      return this.pnoStore.pnosColors.filter(color =>
        Object.values(color).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableUpholstery() {
      return this.pnoStore.pnosUpholstery.filter(upholstery =>
        Object.values(upholstery).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tableOptions() {
      return this.pnoStore.pnosOptions.filter(option =>
        Object.values(option).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    tablePackages() {
      return this.pnoStore.pnosPackages.filter(pkg =>
        Object.values(pkg).some(value =>
          String(value).toLowerCase().includes(this.searchTerm.toLowerCase())
        )
      ).sort((a, b) => {
        if (a[this.sortColumn] === undefined || a[this.sortColumn] === null) return 1;
        if (b[this.sortColumn] === undefined || b[this.sortColumn] === null) return -1;
        if (a[this.sortColumn] < b[this.sortColumn]) return -1 * this.sortOrder;
        if (a[this.sortColumn] > b[this.sortColumn]) return 1 * this.sortOrder;
      });
    },
    isFormValid() {
      return this.newEntry.CustomName && this.newEntry.CustomCategory && this.newEntry.StartDate && this.newEntry.EndDate;
    },
  },
  methods: {

    async refreshModelyear() {
      await this.pnoStore.setModelYear(this.model_year)
      await this.entitiesStore.setModelYear(this.model_year)
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
      this.customFeatureTable = false;
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
        if (this.displaytable === 'Packages') {
          await this.pnoStore.fetchPnosPackages(this.model, this.engine, this.salesversion, this.gearbox);
          console.log('PNO Packages fetched');
        }
      } catch (error) {
        console.error('Error fetching data', error);
      }
    },

    async fetchDiscounts(pno) {
      this.discountTable = true;
      this.activeSalesChannel = {
        Code: pno.Code,
        ChannelName: pno.ChannelName,
        ChannelID: pno.ID
      };
      try {
        await this.entitiesStore.fetchDiscounts(pno.ID);
        console.log('Discounts fetched');
      } catch (error) {
        console.error('Error fetching data', error);
      }
    },

    async fetchXCodes(pno) {
      this.selectedRow = pno.id;
      this.xCodesTable = true;
      this.activeSalesChannel = {
        Code: pno.Code,
        ChannelName: pno.ChannelName,
        ChannelID: pno.ID
      };
      try {
        await this.entitiesStore.fetchCustomLocalOptions(pno.ID);
        console.log('X codes fetched');
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
      this.discountTable = false;
      this.xCodesTable = false;
      this.selectedRow = null;
      this.newsaleschannel = [];
      this.newdiscount = [];
      this.newcustomlocaloption = [];
      this.searchTerm = '';
      await this.pnoStore.setModelYear('0');
    },
    async displaytablereset() {
      this.model_year = '0';
      this.model = '';
      this.engine = '';
      this.salesversion = '';
      this.gearbox = '';
      this.customFeatureTable = false;
      this.discountTable = false;
      this.xCodesTable = false;
      this.selectedRow = null;
      this.newsaleschannel = [];
      this.newdiscount = [];
      this.newcustomlocaloption = [];
      this.searchTerm = '';
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
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdateFeature(this.model, pno.Code, pno.CustomName, pno.CustomCategory, pno.ID)
      pno.edited = false
    },
    async deleteCustomFeature(pno) {
      await this.pnoStore.deleteCustomFeature(this.model, pno.ID)
      pno.edited = false
      await this.pnoStore.fetchPnosFeatures(this.model, this.engine, this.salesversion, this.gearbox)
    },
    pushUpdateOption(pno) {
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdateOption(this.model, pno.Code, pno.CustomName)
      pno.edited = false
    },
    pushUpdateColor(pno) {
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdateColor(this.model, pno.Code, pno.CustomName)
      pno.edited = false
    },
    pushUpdateUpholstery(pno) {
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdateUpholstery(this.model, pno.Code, pno.CustomName, pno.CustomCategory)
      pno.edited = false
    },
    pushUpdateOption(pno) {
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdateOption(this.model, pno.Code, pno.CustomName)
      pno.edited = false
    },
    pushUpdatePackage(pno) {
      if (this.model === '' && (pno.CustomName === '' || pno.CustomName === '*Model-specific text*')) {
        return;
      }
      this.pnoStore.pushUpdatePackage(this.model, pno.Code, pno.CustomName)
      pno.edited = false
    },
    // Custom features
    showCustomFeatureTable() {
      this.customFeatureTable = !this.customFeatureTable;
    },
    pushNewCustomFeature(newEntry) {
      this.pnoStore.pushNewCustomFeature(this.model, newEntry.CustomName, newEntry.CustomCategory, newEntry.StartDate, newEntry.EndDate)
      this.newEntry = {
        CustomName: null,
        CustomCategory: null,
        StartDate: null,
        EndDate: null,
      };
    },
    // Sales Channels
    async pushUpdateSalesChannel(pno) {
      await this.entitiesStore.pushUpdateSalesChannel(pno.ID, pno.Code, pno.ChannelName, pno.Comment, pno.StartDate, pno.EndDate)
      pno.edited = false
    },
    async createSalesChannel(pno) {
      pno.ID = null
      await this.entitiesStore.pushUpdateSalesChannel(pno.ID, pno.Code, pno.ChannelName, pno.Comment, pno.StartDate, pno.EndDate)
      pno.edited = false
      this.newsaleschannel = [];
      await this.entitiesStore.fetchSalesChannels().then(() => {
        console.log('Sales channels fetched')
      }).catch((error) => {
        console.error('Error fetching sales channels', error)
      })
    },
    async deleteSalesChannel(pno) {
      await this.entitiesStore.deleteSalesChannel(pno.ID)
      pno.edited = false
      await this.entitiesStore.fetchSalesChannels().then(() => {
        console.log('Sales channels fetched')
      }).catch((error) => {
        console.error('Error fetching sales channels', error)
      })
    },
    // Discounts
    async pushUpdateDiscount(pno) {
      await this.entitiesStore.pushUpdateDiscount(pno.ID, pno.ChannelID, pno.DiscountPercentage, pno.RetailPrice, pno.WholesalePrice, pno.PNOSpecific, pno.AffectedVisaFile)
      pno.edited = false
    },
    async createDiscount(pno) {
      pno.ID = null
      await this.entitiesStore.pushUpdateDiscount(pno.ID, this.activeSalesChannel.ChannelID, pno.DiscountPercentage, pno.RetailPrice, pno.WholesalePrice, pno.PNOSpecific, pno.AffectedVisaFile)
      pno.edited = false
      this.newdiscount = [];
      await this.entitiesStore.fetchDiscounts(this.activeSalesChannel.ChannelID).then(() => {
        console.log('Discounts fetched')
      }).catch((error) => {
        console.error('Error fetching discounts', error)
      })
    },
    async deleteDiscount(pno) {
      await this.entitiesStore.deleteDiscount(pno.ID)
      pno.edited = false
      await this.entitiesStore.fetchDiscounts(this.activeSalesChannel.ChannelID).then(() => {
        console.log('Discounts fetched')
      }).catch((error) => {
        console.error('Error fetching discounts', error)
      })
    },
    // XCodes
    async pushUpdateXCode(pno) {
      this.entitiesStore.pushUpdateCustomLocalOptions(pno.ID, this.activeSalesChannel.ChannelID, pno.FeatureCode, pno.FeatureRetailPrice, pno.FeatureWholesalePrice)
      pno.edited = false
    },
    async createXCode(pno) {
      pno.ID = null
      await this.entitiesStore.pushUpdateCustomLocalOptions(pno.ID, this.activeSalesChannel.ChannelID, pno.FeatureCode, pno.FeatureRetailPrice, pno.FeatureWholesalePrice)
      pno.edited = false
      this.newcustomlocaloption = [];
      await this.entitiesStore.fetchCustomLocalOptions(this.activeSalesChannel.ChannelID).then(() => {
        console.log('X codes fetched')
      }).catch((error) => {
        console.error('Error fetching X codes', error)
      })
    },
    async deleteXCode(pno) {
      await this.entitiesStore.deleteCustomLocalOptions(pno.ID)
      pno.edited = false
      await this.entitiesStore.fetchCustomLocalOptions(this.activeSalesChannel.ChannelID).then(() => {
        console.log('X codes fetched')
      }).catch((error) => {
        console.error('Error fetching X codes', error)
      })
    },
    deleteVISAFile(file_name) {
      this.entitiesStore.deleteVISAFile(file_name)
    },
    addSalesChannel() {
      this.newsaleschannel.push({ Code: '', ChannelName: '', Comment: '', StartDate: '', EndDate: '', edited: true });
    },
    addDiscount() {
      this.newdiscount.push({ DiscountPercentage: '', RetailPrice: '', WholesalePrice: '', AffectedVisaFile: '', PNOSpecific: '', edited: true });
      this.entitiesStore.fetchDiscounts(this.activeSalesChannel.ChannelID).then(() => {
        console.log('Discounts fetched')
      }).catch((error) => {
        console.error('Error fetching discounts', error)
      })
    },
    addCustomLocalOption() {
      this.newcustomlocaloption.push({ FeatureCode: '', FeatureRetailPrice: '', FeatureWholesalePrice: '', edited: true });
    },
    handleSelectChange(pno) {
      if (pno.AffectedVisaFile.includes('All')) {
        pno.AffectedVisaFile = 'All';
      } else {
        pno.AffectedVisaFile = pno.AffectedVisaFile.join(',');
      }
      pno.edited = true;
      this.pushUpdateDiscount(pno);
    },
    handleSelectChangeNew(pno) {
      if (pno.AffectedVisaFile.includes('All')) {
        pno.AffectedVisaFile = 'All';
      } else {
        pno.AffectedVisaFile = pno.AffectedVisaFile.join(',');
      }
      pno.edited = true;
    },
    //Sorting Functions
    sortTable(column, sortOrder) {
      this.sortOrder = sortOrder;
      this.sortColumn = column;
    },
    // Database updates 
    uploadVisa() {
      const file = this.$refs.file.files[0];
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

th {
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
.engine,
.salesversion,
.gearbox,
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
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 10px;
  display: flex;
  align-items: center;
}

.selected {
  background-color: lightblue;
}
</style>