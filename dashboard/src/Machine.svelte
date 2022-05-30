<script>
    import { locateIP } from "./locator.js";
    export let machine;

    locateIP(machine).then((address_info) => {
        machine.info.city = address_info.city;
        machine.info.country = address_info.country;
        machine.info.latitude = address_info.lat;
        machine.info.longitude = address_info.lon;
        machine.info.region = address_info.region;
        machine.info.zipcode = address_info.zipcode;
        return machine.info;
    });

    let last_seen = machine.last_seen;
    console.log(last_seen);
    console.log(machine);
    function locate() {
        // open tab at address
        window.open(
            `http://maps.google.com/maps?z=12&t=m&q=loc:${machine.info.latitude}+${machine.info.longitude}`
        );
    }
</script>

<div class="entry">
    <span class="ip">{machine.source_ip}</span>
    <span class="last-seen">
        Last seen: {last_seen
            ? last_seen.replace("T", " ").slice(0, -5) + " UTC"
            : "No data"}
    </span>

    {#if machine.info.city}
        <span class="city"
            >Traced to <button on:click={locate}>{machine.info.city}</button
            ></span
        >
    {:else}
        <span class="city">Can't find location</span>
    {/if}

    <div class="info">
        <span>kernel: {machine.info.kernel}</span>
        <span>hostname: {machine.info.hostname}</span>
        <span>uid: {machine.info.uid}</span>
        <span>pipeline: {machine.info.pipeline_status}</span>
        <span>licence: {machine.info.licence}</span>
        <span>system: {machine.info.system_type}</span>
    </div>
</div>

<style>
    .entry {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 0.5em;
        border-bottom: 1px solid #ccc;
    }

    .ip {
        font-weight: bold;
    }

    .last-seen {
        color: #999;
    }

    .city {
        color: #999;
    }

    .info {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-end;
        font-size: 0.7em;
    }

    button {
        background: #ff3e00;
        color: #fff;
        padding: 0.5em;
        margin-left: 0.5em;
        border: none;
        border-radius: 3px;
        font-size: 1em;
        cursor: pointer;
    }
</style>
