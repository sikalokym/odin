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
      <router-link to="/" active-class="active-link">Home</router-link>
      <router-link to="/database" active-class="active-link">View Database</router-link>
      <router-link to="/documents" active-class="active-link">Export Documents</router-link>
    </ul>
</div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
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

.nav-links a.active-link {
  text-decoration: underline;
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