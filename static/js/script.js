/* Preloader fadeout when page is loaded */
window.onload = function() {
    const preloader = document.querySelector('#preloader');
    preloader.classList.add('fadeout');
    setTimeout(function(){
        preloader.style.display = 'none';
    }, 300);
} /* There might be a simplier way to do it, I just got help from here : https://stackoverflow.com/questions/19838955/jquery-loading-screen-into-pure-javascript */

/* open menu */
const menuButton = document.querySelector('button.menu-button');
menuButton.addEventListener('click', () => {
    menuButton.classList.toggle('active')
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
    if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
setTimeout(() => {
    document.querySelector('.flashes').classList.add('hidden')
}, 3000)

/* display profile social network field on click */
const socialIcon = document.querySelector('.social-networks li');
socialIcon.addEventListener('click', (event) => {
    event.preventDefault();
    this.document.querySelector('label').classList.toggle('active')
});

/* animation logo fields */
const loginField = document.querySelector('.text input');
loginField.addEventListener('focus', event => {
    console.log('focus')
    event.target.parent.classList.add('active', 'complete')
})
loginField.addEventListener('blur', event => {
    if(event.target.value === '') {
    event.target.classList.remove('completed', 'active')
    }
})

