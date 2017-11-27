/* open menu */
const menuButton = document.querySelector('button.menu-button');
menuButton.addEventListener('click', () => {
    menuButton.classList.toggle('active');
});

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
    if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
setTimeout(() => {
    document.querySelector('.flashes').classList.add('hidden');
}, 3000);