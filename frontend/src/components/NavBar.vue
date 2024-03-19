<template>
  <nav class="navbar">
    <div class="nav-logo">
      <img src="@/assets/pmt_logo.png" alt="Logo">
      <span class="name">Product Management Tool</span>
    </div>
    <div class="brand-logo">
      <img src="@/assets/brand_logo.svg" alt="brand-logo">
    </div>
    <div class="linkcountry">   
    <ul class="nav-links">
    <router-link to="/">Home</router-link>
    <router-link to="/database">View Database</router-link>
    <router-link to="/documents">Export Documents</router-link>
    </ul>
    <div class="country">
    <label for="country">Country</label>
    <select v-model="selectedCountry" @change="changeCountry(selectedCountry)">
      <option disabled value="">Germany</option>
      <option v-for="country in countries" :key="country" :value="country">
        {{ country }}
      </option>
    </select>
  </div>
</div>
  </nav>
</template>

<script>
  import { usePNOStore } from '../stores/pno.js'

export default {
  name: 'NavBar',
  data() {
    return {
      selectedCountry: '',
      countries: [] // Add your countries here
    };
  },
  methods: {
    changeCountry(newCountry) {
      const pnoStore = usePNOStore();
      pnoStore.setCountry(newCountry);
    },
  }
};
</script>

<style scoped>
.navbar {
  height: 50px;
  background-color: #C8C9C7;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
}

.name {
  font-size: 18px;  
  color: rgb(0, 0, 0);
  margin-left: 1rem;
  top: 2.4rem;
  white-space: nowrap;
}

.nav-logo {
  display: flex;
  align-items: center;
}

.nav-logo img {
  height: 3rem; /* Adjust as per your logo's aspect ratio */
}

.linkcountry {
  display: flex;
  gap: 2rem; /* Adjust as needed */
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1rem;
  right: 7%;
  margin-right: 1rem;
  white-space: nowrap;
}


.nav-links a {
  color: rgb(0, 0, 0);
  text-decoration: none;
  transition: color 0.3s ease;
}

.nav-links a:hover {
  color: #888B8D;
}

.brand-logo img {
  height: 6rem; /* Adjust as per your logo's aspect ratio */
  top: -5px;
  left: 50%;
  transform: translate(-50%);
  display: block;
  position: absolute;
  justify-content: center;
}

.country {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  color: black;
  font-size: 0.8em;
  margin-left: 1rem;
}
    
@media (max-width: 1100px) {
  .brand-logo img {
  display: none;
}
}

@media (max-width: 790px) {
  .name {
  display: none;
}
}

</style>