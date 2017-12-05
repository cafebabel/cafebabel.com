/* Preloader fadeout when page is loaded */
var preloader = document.querySelector('#preloader')
preloader.classList.add('fadeout')
setTimeout(() => {
    preloader.classList.add('hidden')
}, 300)

/* open menu */
const menuButton = document.querySelector('button.menu-button')
menuButton.addEventListener('click', () => {
    menuButton.classList.toggle('active')
})

/* external link in new tab */
Array.from(document.querySelectorAll('a')).forEach(a => {
    if (a.href.search(/\w+:\/\//) === 0 && a.hostname !== location.hostname) a.setAttribute('target', '_blank')
})

/* animation flash info */
const flashes = document.querySelector('.flashes')
if (flashes) {
    setTimeout(() => {
        flashes.classList.add('hidden')
    }, 3000)
}

/* display profile social network field on click */
const socialIcons = Array.from(document.querySelectorAll('.social-networks li'))
if (socialIcons) {
    socialIcons.forEach(socialIcon => {
        socialIcon.querySelector('a').addEventListener('click', (event) => {
            event.preventDefault()
            socialIcons.forEach((li) => li.classList.remove('active'))
            socialIcon.classList.add('active')
        })
    })
}

/* animation login fields */
Array.from(document.querySelectorAll('.authentication-form > div > input')).forEach(input => {
    const parent = input.parentElement
    input.addEventListener('change', () => {
        parent.classList.add('active', 'completed')
    })
    input.addEventListener('focus', () => {
        parent.classList.add('active', 'completed')
    })
    input.addEventListener('blur', () => {
        if (input.value) return
        parent.classList.remove('active', 'completed')
    })
})
