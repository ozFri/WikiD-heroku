import App from './App.svelte';
import Counter from './Counter.svelte';

const app = new App({
  // target: document.querySelector('#agree-votes'),
  target: document.body,
  hydrate: true,
  props: {
  }
});

const test = new Counter({
  // target: document.querySelector('#agree-votes'),
  target: document.querySelector("#agree-votes"),
  hydrate: true,
  props: {
  }
});

export default { app, test };
