<template>
  <main class="main-content">
    <h1>Welcome to the Product Management Tool</h1>
  </main>
</template>

<script>
export default {
  name: 'HomeView'
};
</script>

<style scoped>
.main-content {
  font-size: 26px;
  color: rgb(0, 0, 0);
  position: fixed;
  bottom: 0px;
  right: 40px;
  white-space: nowrap;
  overflow: hidden;
}

@media (max-width: 900px),
(max-height: 570px) {
  .main-content {
    display: none;
  }
}
</style>