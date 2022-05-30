import { writable } from 'svelte/store'

let wsUri = () => {
    var loc = window.location,
        new_uri;
    if (loc.protocol === "https:") {
        new_uri = "wss:";
    } else {
        new_uri = "ws:";
    }
    new_uri += "//" + loc.host;
    new_uri += loc.pathname + "api/ws";
    return new_uri;
};


const webSock = () => {
    let socket = new WebSocket(wsUri());
    const machines = writable([]);

    const getMachines = () => {
      return machines;
    }

    socket.onopen = (e) =>  {
      console.log("[open] Connection established");
      console.log("Sending to server");
    };

    socket.onmessage = (event) =>  {
      let data = Object.values(JSON.parse(event.data))
      console.log(data)
      if (data) {
        machines.set(data);
        console.log(machines)
      }

    };

    socket.onclose = (event) => {
      console.log(event.reason);
    };

    socket.onerror = (error) =>  {
      console.log(`[error] ${error.message}`);
    };

    const sendMessage = () => {
      var msg = {
        'data': 'hello'
      };
      console.log(msg);
      socket.send(JSON.stringify(msg));
    }

    return {getMachines};
  };

export default webSock;