async function getCoderData() {
    var input = document.querySelector('#input');
    var heading = document.querySelector('#joke')
    
    // The await keyword lets js know that it needs to wait until it gets a response back to continue.
    var response = await fetch('https://v2.jokeapi.dev/joke/Any')
        
       
    // We then need to convert the data into JSON format.
    var coderData = await response.json();
    console.log(coderData)
    if (coderData.type == 'single'){

        heading.innerText = coderData.joke
    }
    if (coderData.type == 'twopart'){
        heading.innerText = `${coderData.setup}` + '\n' +`${coderData.delivery}`
    }
    return coderData
}

