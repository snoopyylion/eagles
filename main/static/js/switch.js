let body = document.querySelector('body')
let david = document.querySelector('.david')
let icon = document.querySelector('.bi-moon-fill')

david.addEventListener('click', ()=>{
    body.classList.toggle('dark')
    if(body.classList.contains('dark')){
        icon.classList.replace('bi-moon-fill', 'bi-sun-fill')
    }
    else{
        icon.classList.replace('bi-sun-fill', 'bi-moon-fill')
    }
})