function getNewDog() {
	var url = "https://dog.ceo/api/breed/bulldog/images/random"

	console.log("making fetch to", url)
	
	fetch(url)
		.then(resp=>{return resp.json()})
		.then(json=>{
			console.log(json)

			document.getElementById("dogImage").src = json.message
		})

}


document.addEventListener("DOMContentLoaded", () => {
  console.log("Hello World!");
});
