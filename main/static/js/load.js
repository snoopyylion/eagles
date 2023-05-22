const loader = document.querySelector('.loader-con')
window.addEventListener('load', function(){
    this.setTimeout(myload, 2000)
})
function myload(){
    loader.style.display = 'none';
    document.body.style.overflow = 'auto';
}