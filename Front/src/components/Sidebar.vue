<template>
  <div class="sidebar">
    <h2>Навигация</h2>
    <nav>
      <ul>
        <li><router-link to="/">Карта</router-link></li>
        <li><router-link to="/table">Таблица</router-link></li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
</script>

<style scoped>
.sidebar {
  width: 300px;
  background-color: #f8f9fa;
  padding: 1rem;
  border-right: 1px solid #ccc;
  overflow-y: auto;
  height: 100vh;
  box-sizing: border-box;
}

nav ul {
  padding: 0;
  list-style: none;
  margin-bottom: 1rem;
}

nav ul li {
  margin: 0.5rem 0;
}

nav ul li a {
  text-decoration: none;
  color: #007bff;
}

nav ul li a.router-link-active {
  font-weight: bold;
  color: #0056b3;
}
</style>
