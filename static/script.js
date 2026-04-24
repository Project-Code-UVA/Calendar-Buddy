console.log("calendar js loaded");
"use strict";

const datetxtEl = document.querySelector('.datetxt');
const filteredDateEl = document.querySelector('.filteredDate');
const noEventsMsg = document.getElementById("noEventsMsg");const datesEl = document.querySelector('.dates');
const btnEl = document.querySelectorAll('.calendar_headings .fa-solid');
const todayBtn = document.getElementById('todayBtn');
const monthYearEl = document.querySelector('.month_year')


let dmObj = {
    days: [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ],

    months: [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
        
};

let dateObj = new Date();

let dayName = dmObj.days[dateObj.getDay()];
let month = dateObj.getMonth(); 
let year = dateObj.getFullYear();
let date = dateObj.getDate();

console.log(dayName, month, year, date);

datetxtEl.innerHTML = `${dayName}, ${dmObj.months[month]} ${date}, ${year}`;

filteredDate.innerHTML = `Today: ${dmObj.months[month]} ${date}, ${year}`;


//calendar functionality
const displayCalendar = ()=>{
    let firstDayofMonth = new Date (year, month, 1).getDay();
    let lastDateofLastMonth = new Date (year, month,0).getDate();

    let lastDateofMonth = new Date (year,month+1,0).getDate();
     let lastDayofMonth = new Date (year, month, lastDateofMonth).getDay();
    let days = ""; 

    //previous month days
        for (let i = firstDayofMonth; i>0; i--){
            days += `<li class ="notToday prevM">${lastDateofLastMonth-i+1}</li>`;
        }
        
    //this month
    for (i =1; i <= lastDateofMonth; i++){

        let checkToday = 
        i === dateObj.getDate() && 
        month === new Date().getMonth() && 
        year === new Date().getFullYear()
            ? "today"
            :"notToday";
        
        days += `<li class = ${checkToday}>${i}</li>`;
     }   

     //next month days
     for (let i = lastDayofMonth; i <6; i ++){
         days += `<li class ="notToday nextM">${i-lastDayofMonth+1}</li>`;
     }

    datesEl.innerHTML = days;
    monthYearEl.innerHTML = `${dmObj.months[month]} ${year}`;
}

displayCalendar();


const dateItems = document.querySelectorAll(".dates li");
const eventRows = document.querySelectorAll("#filteredTable tbody tr");
const filteredTableEl = document.getElementById("filteredTable");
const tableHead = filteredTableEl.querySelector("thead");

//previous and next month buttons
btnEl.forEach((btns) =>{
    btns.addEventListener('click', ()=>{
        month = btns.id ==="prev" ? month -1 : month +1;
        
        
        if (month <0 || month>11){
            date = new Date (year, month, new Date().getDate());
            year = date.getFullYear();
            month = date.getMonth();
        } else{
            date = new Date();
        }

        displayCalendar();
    });
});

//today button
todayBtn.addEventListener('click', ()=>{
    dateObj = new Date();
    month = dateObj.getMonth();
    year = dateObj.getFullYear();
    
    filteredDate.innerHTML = `Today: ${dmObj.months[month]} ${dateObj.getDate()}, ${year}`;
    displayCalendar();
});

// buttons for each date

datesEl.addEventListener("click", function (e) {
    if (!e.target.matches("li")) return;

    const clickedEl = e.target;
    const clickedDay = clickedEl.textContent.trim();
    let selectedMonth = month;
    let selectedYear = year;

    
    if (clickedEl.classList.contains("prevM")){
         selectedMonth -= 1;
        if (selectedMonth < 0) {
            selectedMonth = 11;
            selectedYear -= 1;
        }
    } else if( clickedEl.classList.contains("nextM")){
       selectedMonth += 1;
        if (selectedMonth > 11) {
            selectedMonth = 0;
            selectedYear += 1;
        }
    } 


const selectedDate = `${selectedYear}-${String(selectedMonth + 1).padStart(2, "0")}-${String(clickedDay).padStart(2, "0")}`;
    

    console.log("Filtering for:", selectedDate);

    // reset only real days
    document.querySelectorAll(".dates li").forEach(d => {
        if (!d.classList.contains("dummy")) {
            d.classList.remove("today");
            d.classList.add("notToday");
        }
    });
    
    clickedEl.classList.remove("notToday");
    clickedEl.classList.add("today");

    document.getElementById("filteredDate").innerHTML =`Date: ${dmObj.months[selectedMonth]} ${clickedDay}, ${selectedYear}`;

    filterEvents(selectedDate);
});

  //filter on load
dateObjONE = new Date();
monthONE = dateObjONE.getMonth();
yearONE = dateObjONE.getFullYear();
const oneTimeUse = `${yearONE}-${String(monthONE + 1).padStart(2, "0")}-${String(dateObjONE.getDate()).padStart(2, "0")}`;

filterEvents(oneTimeUse);

//filter function
function filterEvents(selectedDate) {
    let found = false;

    eventRows.forEach(row => {
        const rowDate = row.dataset.date.trim();

        if (rowDate === selectedDate) {
            row.style.display = "table-row";
            found = true;
        } else {
            row.style.display = "none";
        }
    });

    if (!found) {
        console.log("No events for this date");
        noEventsMsg.style.display = "block";
        noEventsMsg.innerHTML = `No events today`;
       filteredTableEl.style.display = "none";   // hides whole table
        tableHead.style.display = "none"; 
    } else {
        noEventsMsg.innerHTML = `Your events today: `;
         filteredTableEl.style.display = "table";
        tableHead.style.display = "table-header-group";
    }
    
}
