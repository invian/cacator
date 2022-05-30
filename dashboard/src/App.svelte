<script>
	import Machine from "./Machine.svelte";

	let machines = [];

	fetch("/api/data")
		.then((res) => res.json())
		.then((data) => {
			machines = Object.values(data);
		});
</script>

<main>
	<h1>beacon listener</h1>

	{#each machines as machine}
		<Machine {machine} />
	{/each}
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 2em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
