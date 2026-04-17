console.log("calendar js loaded");
"use strict";

const datetxtEl = document.querySelector('.datetxt');
const datesEl = document.querySelector('.dates');
const btnEl = document.querySelectorAll('.calendar_headings .fa-solid');
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


