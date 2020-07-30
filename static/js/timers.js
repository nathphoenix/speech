// document.writeln("<span id=\"time_online1\"></span>");
// zi_inceput1 = new Date();
// ceas_start1 = zi_inceput1.getTime();

// function initStopwatch1() {
//     var timp_pe_pag1 = new Date();
//     return ((timp_pe_pag1.getTime() + (1000 * 0) - ceas_start1) / 1000);
// }
// var tim = 15;
// function getSecs1() {
//     var tSecs1 = Math.round(initStopwatch1());
//     if((tim-tSecs1)>=0)
//     {
//     var iSecs1 = (tim-tSecs1) % 60;
    
//     var iMins1 = Math.round((tSecs1 - 30) / 60);
//     var iHour1 = Math.round((iMins1 - 30) / 60);
//     var iMins1 = iMins1 % 60;
//     var min = Math.floor((tim-tSecs1) / 60);
//     var iHour1 = iHour1 % 24;
//     var sSecs1 = "" + ((iSecs1 > 9) ? iSecs1 : "0" + iSecs1);
//     var sMins1 = "" + ((iMins1 > 9) ? iMins1 : "0" + iMins1);
//     var sHour1 = "" + ((iHour1 > 9) ? iHour1 : "0" + iHour1);
//     document.getElementById('time_online1').innerHTML = min + ":" + sSecs1;
//     window.setTimeout('getSecs1()', 1000);
// }
// else
//     alert("time up");
// }
// window.setTimeout('getSecs1()', 1000)

console.log('working...')