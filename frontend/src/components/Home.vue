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
  position: absolute;
  bottom: 2.4rem;
  right: 2.4rem;
  }
  
@media (max-width: 1280px), (max-height: 768px) {
  .main-content {
  display: none;
  }
}

  </style>
  