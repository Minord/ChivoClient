
//Host URL
host_url = 'http://diego.laptop:8085'

async function reqjson(route){
	let response = await fetch(host_url + route);
	let json = await response.json();
	return json
}

async function reqtext(route){
	let response = await fetch(host_url + route);
	let text = await response.text();
	return text
}

async function posreq(route, data){
	let response = await fetch(host_url + route,
							 {method : "POST",
							  headers : {
							      "Content-Type" : "application/json"
							  },
							  body: JSON.stringify(data)});
}

async function req(route){
	let response = await fetch(host_url + route);
}

async function balance(){return await reqjson('/balance');}
async function realBalance(){return await reqjson('/real-balance');}
async function price(){return await reqtext('/price');}
async function realPrice(){return await reqtext('/real-price');}
async function sellon(){return await reqjson('/sellon');}
async function sellonReset(){return await req('/sellonreset')}
async function buyUSD(){return await reqtext('/buyUSD');}
async function buyBTC(){return await reqtext('/buyBTC');}

async function sellonSet(data){posreq('/sellonset', data);}



//Balance and Prices
async function updateBalanceElement(real = false){
	let balancet = await balance();
	if (real){
		balancet = await realBalance();
	}
	document.getElementById('usd-label').textContent = balancet['USD'].toFixed(2);
	document.getElementById('btc-label').textContent = balancet['BTC'].toFixed(8);
	document.getElementById('btcuds-label').textContent = balancet['BTCUSD'].toFixed(2);
}

async function updatePriceElement(real = false){
	let pricetemp = await price();
	if (real) { 
		pricetemp = await realPrice();
	}
	document.getElementById('chivo-price').textContent = parseFloat(pricetemp).toFixed(2);
}

async function updateChivoPriceButton(){
	await updatePriceElement(real = true);
}

//Buy Buttons
function enableBuy(){
	document.getElementsByClassName("btc")[0].disabled = false;
	document.getElementsByClassName("usd")[0].disabled = false;
}

function disableBuy(){
	document.getElementsByClassName("btc")[0].disabled = true; document.getElementsByClassName("usd")[0].disabled = true;
}

async function disabledBuyTemp(){
	//This depends on last transaccion time stamp
	//Need to make request to server
	disableBuy();
	let sellont = await sellon();
	let lastTransaction = await sellont['last-buy-stamp'];
	updateBalanceElement();	
	updatePriceElement();
	let i = setInterval(function(){
		let seconds = (Date.now() - lastTransaction) / 1000;
		let secondsint = parseInt(60*3 - seconds);
		document.getElementById('timer').textContent = 
			`${Math.floor(secondsint/60)}:${((secondsint)%60).toString().padStart(2, '0')}`;
		if (seconds > 60*3){
			document.getElementById('timer').textContent = "0:00";
			clearInterval(i);
			enableBuy();
		}
		if (Math.floor(seconds) == 62){
			updatePriceElement(real = true);
			updateBalanceElement(real = true);	
		}

	} ,1000);
}

async function checkSellOn(){
	let last_sellon_state = false;
	let loop = setInterval(async function(){
		let actual_sellon_state = await sellon();
		if (last_sellon_state != actual_sellon_state["active-sellon"]){
			updatePriceElement();
			updateBalanceElement();
			updateSellOnState();
			last_sellon_state = actual_sellon_state["active-sellon"];
		}		
	}, 10 * 1000);
}

//Button Actions of Buy
async function buyBTCbutton() {
	disableBuy();
	await buyBTC();
	disabledBuyTemp();
}

async function buyUSDbutton() {
	disableBuy();
	await buyUSD();
	disabledBuyTemp();
}





//Set On Buttons and controllers

async function setSellOn(){
	document.getElementById("reset").disabled = false;

	priceToSell = document.getElementById('price-to-sell').value;
	priceToSell = parseFloat(priceToSell);
	await sellonSet({
		"sellon-price" : priceToSell,
	});

	document.getElementById("price-to-sell").value = "";
	document.getElementById("price-to").textContent = parseFloat(priceToSell).toFixed(2);
	updatePriceToSellButton();
}

async function resetSellOn(){
	document.getElementById("reset").disabled = true;
	await sellonReset();
	document.getElementById("price-to").textContent = "0.00";
}


//Disable set if no number is on input
function validateNumber(event) {
    var key = window.event ? event.keyCode : event.which;
	updatePriceToSellButton();
    if (event.keyCode === 8 || event.keyCode === 46) {
        return true;
    } else if ( key < 48 || key > 57 ) {
        return false;
    } else {
        return true;
    }
}

function updatePriceToSellButton(){
	if (document.getElementById("price-to-sell").value === '') {
	  document.getElementById("set").disabled = true;
	} else {
	  document.getElementById("set").disabled = false;
	}
}

async function updateSellOnState(){
	sellon_state = await sellon();
	if (sellon_state["active-sellon"]){
		document.getElementById("reset").disabled = false;
		document.getElementById("price-to").textContent = sellon_state["sellon-price"].toFixed(2);
	}
	else {
		document.getElementById("reset").disabled = true;
	}
}

document.getElementById("reset").disabled = true;
//Executing
disabledBuyTemp();
updateBalanceElement();
updatePriceToSellButton();
updatePriceElement();
updateSellOnState();
checkSellOn();
