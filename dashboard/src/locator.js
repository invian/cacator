let cached_locations = {};


export async function locateIP(machine) {
    if (cached_locations[ machine.source_ip]) {
        console.log('cached', machine.source_ip);
        return cached_locations[machine.source_ip];
    }
    return await fetch(`http://ip-api.com/json/${machine.source_ip}`)
    .then((response) => response.json())
    .then((address_info) => {
        cached_locations[machine.source_ip] = address_info;
        return address_info
    });
}
