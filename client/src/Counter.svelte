<script>
 import { onMount } from "svelte";

 let data = [];

 onMount(async function() {
     const response = await fetch("http://localhost:5000/api");
     const json = await response.json();
     data = json;
 });
</script>
{data}
